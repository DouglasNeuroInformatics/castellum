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

import datetime

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.pseudonyms.forms import PseudonymForm
from castellum.pseudonyms.helpers import get_subject
from castellum.recruitment.mixins import BaseAttributeSetUpdateView
from castellum.recruitment.mixins import BaseCalendarView
from castellum.recruitment.mixins import ParticipationMixin
from castellum.recruitment.models import Appointment
from castellum.recruitment.models import Participation
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Study
from castellum.subjects.mixins import BaseAdditionalInfoUpdateView
from castellum.subjects.mixins import BaseDataProtectionUpdateView


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
        participations = self.study.participation_set\
            .filter(status=Participation.INVITED)\
            .select_related('subject')
        for participation in participations:
            has_access = self.request.user.has_privacy_level(participation.subject.privacy_level)
            context['list'].append((participation, has_access))

        return context


class ParticipationDetailView(
    ParticipationMixin, PermissionRequiredMixin, DetailView
):
    template_name = 'execution/participation_detail.html'
    model = Participation
    permission_required = 'recruitment.view_participation_pseudonyms'
    study_status = [Study.EXECUTION]
    participation_status = [Participation.INVITED]

    def get_object(self):
        return self.participation


class ResolveView(StudyMixin, PermissionRequiredMixin, FormView):
    template_name = 'execution/study_resolve.html'
    permission_required = 'recruitment.view_participation_pseudonyms'
    study_status = [Study.EXECUTION]
    form_class = PseudonymForm

    def form_valid(self, form):
        try:
            subject = get_subject(self.study.domain, form.cleaned_data['pseudonym'])
            participation = Participation.objects.filter(
                study=self.study,
                subject=subject,
                status=Participation.INVITED,
            ).get()
            return redirect('execution:participation-detail', self.study.pk, participation.pk)
        except ObjectDoesNotExist:
            messages.warning(self.request, _('No match found'))
            return self.render_to_response(self.get_context_data(form=form))


class ExecutionUpdateMixin(ParticipationMixin):
    study_status = [Study.EXECUTION]
    participation_status = [Participation.INVITED]

    def get_success_url(self):
        return reverse(
            'execution:participation-detail',
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
        return self.participation.subject.contact


class AttributeSetUpdateView(ExecutionUpdateMixin, BaseAttributeSetUpdateView):
    def get_object(self):
        return self.participation.subject.attributeset


class DataProtectionUpdateView(ExecutionUpdateMixin, BaseDataProtectionUpdateView):
    def get_object(self):
        return self.participation.subject


class AdditionalInfoUpdateView(ExecutionUpdateMixin, BaseAdditionalInfoUpdateView):
    def get_object(self):
        return self.participation.subject


class CalendarView(StudyMixin, PermissionRequiredMixin, BaseCalendarView):
    model = Study
    permission_required = 'recruitment.view_participation'
    study_status = [Study.EXECUTION]
    feed = 'execution:calendar-feed'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = "execution/base.html"
        return context

    def render_appointment(self, appointment):
        return {
            'title': appointment.session.name,
            'start': appointment.start,
            'end': appointment.end,
            'url': reverse('execution:participation-detail', args=[
                self.object.pk, appointment.participation.pk
            ]),
        }

    def get_appointments(self):
        return super().get_appointments().filter(session__study=self.object)


class ReceptionView(PermissionRequiredMixin, ListView):
    model = Appointment
    template_name = 'execution/reception.html'
    permission_required = 'recruitment.search_execution'

    def get_queryset(self):
        return super().get_queryset().filter(
            participation__status=Participation.INVITED,
            start__date=datetime.date.today(),
        ).order_by('start')
