# (c) 2018-2020
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

from django import forms
from django.contrib import messages
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from dateutil.relativedelta import relativedelta

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.recruitment import filter_queries
from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import SubjectFilter
from castellum.subjects.models import Subject
from castellum.utils.views import ReadonlyMixin

from ..forms import ExcludedStudiesForm
from ..forms import SessionForm
from ..mixins import StudyMixin
from ..models import Resource
from ..models import Study
from ..models import StudySession


def get_related_studies(study):
    # if no filters exist, all active studies would be related
    if not SubjectFilter.objects.filter(group__study=study).exists():
        return Study.objects.none()

    dt = timezone.now() - relativedelta(years=2)
    related_prs = ParticipationRequest.objects.filter(
        updated_at__gte=dt,
        status=ParticipationRequest.INVITED,
        subject__in=Subject.objects.filter(filter_queries.study(study))
    )
    return Study.objects\
        .filter(participationrequest__in=related_prs)\
        .annotate(count=models.Count('pk'))\
        .exclude(pk=study.pk)\
        .order_by('-count')[:5]


class StudyRecruitmentSettingsUpdateView(
    StudyMixin, PermissionRequiredMixin, ReadonlyMixin, UpdateView
):
    model = Study
    fields = ('advanced_filtering', 'recruitment_text', 'is_exclusive', 'complete_matches_only')
    permission_required = 'studies.change_study'
    template_name = 'studies/study_recruitmentsettings_form.html'
    tab = 'recruitmentsettings'
    subtab = 'update'

    def get_readonly(self):
        return self.object.status == Study.FINISHED

    def get_success_url(self):
        return reverse('studies:recruitmentsettings', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyExcludedStudiesView(
    StudyMixin, PermissionRequiredMixin, ReadonlyMixin, UpdateView
):
    model = Study
    template_name = 'studies/study_excluded_studies.html'
    form_class = ExcludedStudiesForm
    permission_required = 'studies.change_study'
    tab = 'recruitmentsettings'
    subtab = 'excluded-studies'

    def get_readonly(self):
        return self.object.status == Study.FINISHED

    def get_success_url(self):
        return reverse('studies:excluded-studies', args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = (
            Subject.objects.filter(
                filter_queries.study(self.object),
                filter_queries.has_consent()
            ).count()
        )
        context['total_count'] = Subject.objects.count()
        context['related_studies'] = list(get_related_studies(self.object))
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyExclusionCriteriaView(
    StudyMixin, PermissionRequiredMixin, ReadonlyMixin, UpdateView
):
    model = Study
    template_name = 'studies/study_exclusioncriteria.html'
    fields = ('exclusion_criteria',)
    permission_required = 'studies.change_study'
    tab = 'recruitmentsettings'
    subtab = 'exclusioncriteria'

    def get_readonly(self):
        return self.object.status == Study.FINISHED

    def get_success_url(self):
        return reverse('studies:exclusioncriteria', args=[self.object.pk])

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudySessionsView(
    StudyMixin, PermissionRequiredMixin, ReadonlyMixin, UpdateView
):
    model = Study
    template_name = 'studies/study_sessions.html'
    fields = (
        'session_instructions',
        'sessions_start',
        'sessions_end',
    )
    permission_required = 'studies.change_study'
    tab = 'recruitmentsettings'
    subtab = 'sessions'

    def get_session_form(self):
        return SessionForm(prefix='{prefix}')

    def get_session_formset(self):
        formset_class = forms.modelformset_factory(
            StudySession, form=SessionForm, extra=0, can_delete=True
        )
        kwargs = self.get_form_kwargs()
        study = kwargs.pop('instance', None)
        readonly = kwargs.pop('readonly', False)
        return formset_class(
            queryset=StudySession.objects.filter(study=study),
            form_kwargs={'readonly': readonly},
            **kwargs
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'session_formset' not in context:
            context['session_formset'] = self.get_session_formset()
        context["template_form"] = self.get_session_form()
        context['has_resources'] = Resource.objects.exists()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        session_formset = self.get_session_formset()
        if form.is_valid() and session_formset.is_valid():
            return self.form_valid(form, session_formset)
        else:
            return self.form_invalid(form, session_formset)

    def form_invalid(self, form, session_formset):
        return self.render_to_response(
            self.get_context_data(form=form, session_formset=session_formset)
        )

    def form_valid(self, form, session_formset):
        messages.success(self.request, _('Data has been saved.'))
        response = super().form_valid(form)
        for subform in session_formset:
            subform.instance.study = form.instance
        session_formset.save()
        return response

    def get_readonly(self):
        return self.object.status == Study.FINISHED

    def get_success_url(self):
        return reverse('studies:sessions', args=[self.object.pk])


class StudyMailSettingsView(
    StudyMixin, PermissionRequiredMixin, ReadonlyMixin, UpdateView
):
    model = Study
    template_name = 'studies/study_mailsettings.html'
    fields = (
        'mail_subject',
        'mail_body',
        'mail_reply_address',
    )
    permission_required = 'studies.change_study'
    tab = 'recruitmentsettings'
    subtab = 'mailsettings'

    def get_readonly(self):
        return self.object.status == Study.FINISHED

    def get_success_url(self):
        return reverse('studies:mailsettings', args=[self.object.pk])

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)
