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
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.mixins import BaseContactUpdateView
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
