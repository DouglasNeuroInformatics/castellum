# (c) 2018-2021
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

from django.conf import settings
from django.contrib import messages
from django.forms import modelformset_factory
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
from castellum.recruitment import filter_queries
from castellum.recruitment.forms import SubjectFilterAddForm
from castellum.recruitment.forms import SubjectFilterForm
from castellum.recruitment.forms import SubjectFilterFormSet
from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.subjects.models import Subject

from ..mixins import StudyMixin


class CustomFilterMixin:
    """Should be called *after* PermissionRequiredMixin."""

    def dispatch(self, request, *args, **kwargs):
        if self.study.custom_filter:
            return TemplateResponse(
                request=self.request,
                template='studies/filtergroup_blocked.html',
                context={
                    'study': self.study,
                    'total_count': Subject.objects.count(),
                    'count': (
                        Subject.objects.filter(
                            filter_queries.study(self.object),
                            filter_queries.has_consent(),
                        ).count()
                    ),
                },
            )
        return super().dispatch(request, *args, **kwargs)


class FilterMixin(StudyMixin, PermissionRequiredMixin, CustomFilterMixin):
    tab = 'recruitmentsettings'
    subtab = 'filters'

    def get_permission_required(self):
        permission_required = set(['studies.change_study'])
        permission_required.update(super().get_permission_required())

        max_privacy_level = self.study.get_filter_max_privacy_level()
        if max_privacy_level:
            permission_required.add('castellum_auth.privacy_level_{}'.format(max_privacy_level))

        return permission_required

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.study.is_filter_trial:
            context['base_template'] = 'studies/study_filterpreview_recruitmentsettings_base.html'
        else:
            context['base_template'] = 'studies/study_recruitmentsettings_base.html'
        return context


class FilterGroupListView(FilterMixin, ListView):
    model = SubjectFilterGroup
    template_name = 'studies/filtergroup_advanced.html'
    permission_required = 'studies.change_study'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(study=self.study)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Subject.objects.count()
        context['count'] = (
            Subject.objects.filter(
                filter_queries.study(self.study),
                filter_queries.has_consent()
            ).count()
        )
        context['expected_subject_factor'] = settings.CASTELLUM_EXPECTED_SUBJECT_FACTOR
        context['expected_subject_count'] = (
            self.study.min_subject_count * settings.CASTELLUM_EXPECTED_SUBJECT_FACTOR
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
    permission_required = 'studies.change_study'

    def post(self, *args, **kwargs):
        group = SubjectFilterGroup.objects.create(study=self.study)
        return redirect(group.get_absolute_url())


class FilterGroupUpdateView(FilterMixin, UpdateView):
    model = SubjectFilterGroup
    fields = []
    template_name = "studies/filtergroup.html"
    permission_required = 'studies.change_study'

    def get_object(self):
        return get_object_or_404(SubjectFilterGroup, study=self.study, pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
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
        )

    def get_inaccessible_attributedescriptions(self):
        min_privacy_level = 2
        for member in self.study.members.all():
            if member.has_perm('studies.change_study', obj=self.study):
                privacy_level = member.get_privacy_level(obj=self.study)
                if privacy_level < min_privacy_level:
                    min_privacy_level = privacy_level

        return AttributeDescription.objects.filter(
            subjectfilter__group__study=self.study,
            privacy_level_read__gt=min_privacy_level,
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['count'] = self.object.get_matches().count()

        context['total_count'] = Subject.objects.count()
        context['expected_subject_factor'] = settings.CASTELLUM_EXPECTED_SUBJECT_FACTOR
        context['expected_subject_count'] = (
            self.study.min_subject_count * settings.CASTELLUM_EXPECTED_SUBJECT_FACTOR
        )

        context['inaccessible'] = list(self.get_inaccessible_attributedescriptions())

        context['add_form'] = SubjectFilterAddForm(user=self.request.user)
        context['templates'] = {}
        for description in AttributeDescription.objects.all():
            context['templates'][description.pk] = SubjectFilterForm(
                initial={'description': description}, prefix='{prefix}'
            )

        if 'formset' not in context:
            context['formset'] = self.get_formset()

        return context


class FilterGroupDeleteView(FilterMixin, DeleteView):
    model = SubjectFilterGroup
    template_name = 'studies/filtergroup_confirm_delete.html'
    permission_required = 'studies.change_study'

    def get_object(self):
        return get_object_or_404(SubjectFilterGroup, study=self.study, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('studies:filtergroup-index', args=[self.study.pk])


class FilterGroupDuplicateView(FilterMixin, View):
    permission_required = 'studies.change_study'

    def post(self, request, study_pk, pk):
        original = get_object_or_404(SubjectFilterGroup, study=self.study, pk=pk)
        SubjectFilterGroup.objects.clone(original)
        messages.success(request, _(
            'The filters have been duplicated. You can now edit the duplicate.'))
        return redirect('studies:filtergroup-index', self.study.pk)
