# (c) 2018
#     MPIB <https://www.mpib-berlin.mpg.de/>,
#     MPI-CBS <https://www.cbs.mpg.de/>,
#     MPIP <http://www.psych.mpg.de/>
#
# This file is part of Castellum.
#
# Castellum is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Castellum is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Castellum. If not, see
# <http://www.gnu.org/licenses/>.

from django.contrib import messages
from django.forms import modelformset_factory
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic import View

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.recruitment.forms import SubjectFilterForm
from castellum.recruitment.forms import SubjectFilterFormSet
from castellum.recruitment.forms import SubjectFilterGroupForm
from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.settings import CASTELLUM_EXPECTED_SUBJECT_FACTOR
from castellum.utils.views import ReadonlyMixin

from ..mixins import StudyMixin
from ..model_proxies import Study


class CustomFilterMixin:
    """Should be called *after* PermissionRequiredMixin."""

    def dispatch(self, request, *args, **kwargs):
        if self.study.custom_filter:
            return TemplateResponse(
                request=self.request,
                template='studies/filtergroup_blocked.html',
                context={
                    'study': self.study,
                    'total_count': AttributeSet.objects.count(),
                    'potential_subjects_count': AttributeSet.apply_study_filter(self.study).count(),
                },
            )
        return super().dispatch(request, *args, **kwargs)


class FilterMixin(StudyMixin, PermissionRequiredMixin, CustomFilterMixin):
    def get_permission_required(self):
        permission_required = set()
        permission_required.update(super().get_permission_required())

        max_privacy_level = self.study.get_filter_max_privacy_level()
        if max_privacy_level:
            permission_required.add('castellum_auth.privacy_level_{}'.format(max_privacy_level))

        return permission_required


def subject_count_warnings(request, min_subjects_count, potential_subjects_count):
    if min_subjects_count == 0:
        messages.warning(request, _(
            'Weak recruitment process. '
            'Please, define the number of subjects for this study.'
        ))
    elif potential_subjects_count < min_subjects_count * CASTELLUM_EXPECTED_SUBJECT_FACTOR:
        messages.warning(request, _(
            'For a smooth recruitment process, your institution recommends at least '
            '%(castellum_factor)dx more potential than required subjects '
            '(i.e. %(recommended_count)d for this study). Current amount of potential '
            'subjects: %(potential_count)d'
        ) % {
            'castellum_factor': CASTELLUM_EXPECTED_SUBJECT_FACTOR,
            'recommended_count': min_subjects_count * CASTELLUM_EXPECTED_SUBJECT_FACTOR,
            'potential_count': potential_subjects_count,
        })


class FilterGroupListView(FilterMixin, ListView):
    model = SubjectFilterGroup
    template_name = 'studies/filtergroup_list.html'
    permission_required = 'recruitment.view_subjectfilter'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(study=self.study)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['potential_subjects_count'] = AttributeSet.apply_study_filter(self.study).count()
        subject_count_warnings(
            self.request, self.study.min_subjects_count, context['potential_subjects_count']
        )
        return context

    def get(self, request, *args, **kwargs):
        if self.study.advanced_filtering:
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            return self.render_to_response(context)
        else:
            group, __ = SubjectFilterGroup.objects.get_or_create(study=self.study)
            return redirect(group.get_absolute_url())


class FilterGroupCreateView(FilterMixin, View):
    permission_required = 'recruitment.change_subjectfilter'
    study_modes = [Study.EDIT]

    def post(self, *args, **kwargs):
        group = SubjectFilterGroup.objects.create(study=self.study)
        return redirect(group.get_absolute_url())


class FilterGroupUpdateView(FilterMixin, ReadonlyMixin, UpdateView):
    model = SubjectFilterGroup
    form_class = SubjectFilterGroupForm
    template_name = "studies/filtergroup.html"
    permission_required = 'recruitment.change_subjectfilter'

    def get_object(self):
        return get_object_or_404(SubjectFilterGroup, study=self.study, pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.get_readonly():
            return HttpResponseBadRequest()
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def form_valid(self, form, formset):
        messages.success(self.request, _('Filter update successfull!'))
        formset.save()
        return super().form_valid(form)

    def get_formset(self):
        formset_class = modelformset_factory(
            SubjectFilter,
            form=SubjectFilterForm,
            formset=SubjectFilterFormSet,
            extra=0,
            can_delete=True,
        )
        return formset_class(
            queryset=self.object.subjectfilter_set.all(),
            data=self.get_form_kwargs().get('data'),
            form_kwargs={
                'user': self.request.user,
            },
        )

    def get_readonly(self):
        return self.study.study_mode != Study.EDIT

    def get_inaccessible_attributedescriptions(self):
        min_privacy_level = 2
        for member in self.study.members.all():
            if member.has_perm('recruitment.view_subjectfilter', obj=self.study):
                privacy_level = member.get_privacy_level(obj=self.study)
                if privacy_level < min_privacy_level:
                    min_privacy_level = privacy_level

        return AttributeDescription.objects.filter(
            subjectfilter__group__study=self.study,
            privacy_level_read__gt=min_privacy_level,
        ).distinct()

    def get_context_data(self, **kwargs):
        inaccessible = list(self.get_inaccessible_attributedescriptions())
        if inaccessible:
            messages.warning(self.request, _(
                'At least one member of this study with access to filters does not have a '
                'sufficient privacy level to view the following attributes: %s'
            ) % ', '.join(description.label for description in inaccessible))

        data = super().get_context_data(**kwargs)
        data['count'] = self.object.get_subject_count()
        data['total_count'] = AttributeSet.objects.count()
        data['add_form'] = SubjectFilterForm(user=self.request.user)
        data['templates'] = {}
        for description in AttributeDescription.objects.all():
            data['templates'][description.pk] = SubjectFilterForm(
                user=self.request.user,
                initial={'description': description},
                prefix='{prefix}')

        if 'formset' not in data:
            data['formset'] = self.get_formset()

        if not self.study.advanced_filtering:
            subject_count_warnings(self.request, self.study.min_subjects_count, data['count'])

        return data


class FilterGroupDeleteView(FilterMixin, DeleteView):
    model = SubjectFilterGroup
    template_name = 'studies/filtergroup_confirm_delete.html'
    permission_required = 'recruitment.change_subjectfilter'
    study_modes = [Study.EDIT]

    def get_object(self):
        return get_object_or_404(SubjectFilterGroup, study=self.study, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('studies:filtergroup-index', args=[self.study.pk])


class FilterGroupDuplicateView(FilterMixin, View):
    permission_required = 'recruitment.change_subjectfilter'
    study_modes = [Study.EDIT]

    def post(self, request, study_pk, pk):
        original = get_object_or_404(SubjectFilterGroup, study=self.study, pk=pk)
        SubjectFilterGroup.objects.clone(original)
        messages.success(request, _(
            'The filters have been duplicated. You can now edit the duplicate.'))
        return redirect('studies:filtergroup_index', self.study.pk)
