# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
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
from castellum.recruitment.models import Attribute
from castellum.recruitment.models import Participation
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.subjects.models import Subject

from ..mixins import StudyMixin


class FilterMixin(StudyMixin, PermissionRequiredMixin):
    tab = 'recruitmentsettings'
    subtab = 'filters'
    is_filter_trial = None

    @property
    def base_template(self):
        if self.study.is_filter_trial:
            return 'studies/study_filtertrial_base.html'
        return None

    def get_permission_required(self):
        permission_required = {'studies.change_study'}
        permission_required.update(super().get_permission_required())
        return permission_required


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
        context['count'] = Subject.objects.filter(
            filter_queries.study_recruitable(self.study),
            filter_queries.already_in_study(self.study, include_recruitment=False),
        ).count()
        context['expected_subject_factor'] = settings.CASTELLUM_EXPECTED_SUBJECT_FACTOR

        participating = self.study.participation_set.filter(
            status__in=Participation.INVITED_SET
        ).count()
        still_needed = self.study.min_subject_count - participating
        context['expected_subject_count'] = (
            still_needed * settings.CASTELLUM_EXPECTED_SUBJECT_FACTOR
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
    template_name = 'studies/filtergroup.html'
    permission_required = 'studies.change_study'

    def get_object(self):
        return get_object_or_404(
            SubjectFilterGroup, study=self.study, pk=self.kwargs['pk']
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def form_valid(self, form, formset):
        messages.success(self.request, _('Filter update successfull!'))
        for f in formset.extra_forms:
            f.instance.group = self.object
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['count'] = self.object.get_potential_matches().count()

        context['total_count'] = Subject.objects.count()
        context['expected_subject_factor'] = settings.CASTELLUM_EXPECTED_SUBJECT_FACTOR

        participating = self.study.participation_set.filter(
            status__in=Participation.INVITED_SET
        ).count()
        still_needed = self.study.min_subject_count - participating
        context['expected_subject_count'] = (
            still_needed * settings.CASTELLUM_EXPECTED_SUBJECT_FACTOR
        )

        context['add_form'] = SubjectFilterAddForm()
        context['templates'] = {}
        for attribute in Attribute.objects.all():
            context['templates'][attribute.pk] = SubjectFilterForm(
                initial={'attribute': attribute}, prefix='{prefix}'
            )

        if 'formset' not in context:
            context['formset'] = self.get_formset()

        return context


class FilterGroupDeleteView(FilterMixin, DeleteView):
    model = SubjectFilterGroup
    template_name = 'studies/filtergroup_confirm_delete.html'
    permission_required = 'studies.change_study'

    def get_object(self):
        return get_object_or_404(
            SubjectFilterGroup, study=self.study, pk=self.kwargs['pk']
        )

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
