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

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import ListView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.forms import SearchForm
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.contacts.models import Contact
from castellum.pseudonyms.forms import PseudonymForm
from castellum.pseudonyms.helpers import get_subject
from castellum.recruitment.mixins import BaseAttributeSetUpdateView
from castellum.recruitment.mixins import ParticipationRequestMixin
from castellum.recruitment.models import ParticipationRequest
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Study
from castellum.subjects.mixins import BaseAdditionalInfoUpdateView
from castellum.subjects.mixins import BaseDataProtectionUpdateView
from castellum.utils.views import GetFormView


class StudyListView(LoginRequiredMixin, ListView):
    template_name = 'execution/study_list.html'
    model = Study

    def get_queryset(self):
        qs = super().get_queryset()
        perms = ('recruitment.view_participation_pseudonyms', 'studies.access_study')
        return [study for study in qs.filter(status=Study.EXECUTION) if (
            self.request.user.has_perms(perms, obj=study)
        )]


class StudyDetailView(StudyMixin, PermissionRequiredMixin, DetailView):
    template_name = 'execution/study_detail.html'
    model = Study
    permission_required = 'recruitment.view_participation_pseudonyms'
    study_status = [Study.EXECUTION]

    def get_object(self):
        return self.study

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['list'] = []
        prs = self.study.participationrequest_set\
            .filter(status=ParticipationRequest.INVITED)\
            .select_related('subject')
        for pr in prs:
            has_access = self.request.user.has_privacy_level(pr.subject.privacy_level)
            context['list'].append((pr, has_access))

        return context


class ParticipationRequestDetailView(
    ParticipationRequestMixin, PermissionRequiredMixin, DetailView
):
    template_name = 'execution/participationrequest_detail.html'
    model = ParticipationRequest
    permission_required = 'recruitment.view_participation_pseudonyms'
    study_status = [Study.EXECUTION]
    participationrequest_status = [ParticipationRequest.INVITED]

    def get_object(self):
        return self.participationrequest


class SearchView(LoginRequiredMixin, GetFormView):
    template_name = 'execution/search.html'
    form_class = SearchForm

    def get_matches(self, form):
        contacts = Contact.objects.fuzzy_filter(form.cleaned_data['search'])
        subject_pks = list(contacts.values_list('subject_id', flat=True))
        participation_requests = ParticipationRequest.objects.filter(
            subject_id__in=subject_pks,
            study__status=Study.EXECUTION,
            status=ParticipationRequest.INVITED,
        ).select_related('subject', 'study')

        result = {}
        perms = ('studies.access_study', 'recruitment.view_participation_pseudonyms')
        for pr in participation_requests:
            if (
                self.request.user.has_perms(perms, pr.study) and
                self.request.user.has_privacy_level(pr.subject.privacy_level)
            ):
                pr.can_access = True
                result.setdefault(pr.subject, [])
                result[pr.subject].append(pr)
            elif self.request.user.has_perm('recruitment.search_execution', pr.study):
                result.setdefault(pr.subject, [])
                result[pr.subject].append(pr)

        return list(result.items())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form')
        if form and form.is_valid():
            context['object_list'] = self.get_matches(form)
        return context


class ResolveView(StudyMixin, PermissionRequiredMixin, GetFormView):
    template_name = 'execution/study_resolve.html'
    permission_required = 'recruitment.view_participation_pseudonyms'
    study_status = [Study.EXECUTION]
    form_class = PseudonymForm

    def form_valid(self, form):
        try:
            subject = get_subject(self.study.domain, form.cleaned_data['pseudonym'])
            pr = ParticipationRequest.objects.filter(
                study=self.study,
                subject=subject,
                status=ParticipationRequest.INVITED,
            ).get()
            return redirect('execution:participationrequest-detail', self.study.pk, pr.pk)
        except ObjectDoesNotExist:
            messages.warning(self.request, _('No match found'))
            return super().form_valid(form)


class ExecutionUpdateMixin(ParticipationRequestMixin):
    study_status = [Study.EXECUTION]
    participationrequest_status = [ParticipationRequest.INVITED]

    def get_success_url(self):
        return reverse(
            'execution:participationrequest-detail',
            args=[self.kwargs['study_pk'], self.kwargs['pk']],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = "execution/base.html"
        return context

    def get_permission_required(self):
        permission_required = {'recruitment.view_participation_pseudonyms'}
        permission_required.update(super().get_permission_required())
        return permission_required


class ContactUpdateView(ExecutionUpdateMixin, BaseContactUpdateView):
    def get_object(self):
        return self.participationrequest.subject.contact


class AttributeSetUpdateView(ExecutionUpdateMixin, BaseAttributeSetUpdateView):
    def get_object(self):
        return self.participationrequest.subject.attributeset


class DataProtectionUpdateView(ExecutionUpdateMixin, BaseDataProtectionUpdateView):
    def get_object(self):
        return self.participationrequest.subject


class AdditionalInfoUpdateView(ExecutionUpdateMixin, BaseAdditionalInfoUpdateView):
    def get_object(self):
        return self.participationrequest.subject
