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
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import UpdateView
from django.views.generic import View

from castellum.appointments.helpers import get_reminder_body
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.utils import scheduler
from castellum.utils.mail import MailContext

from ..forms import SessionForm
from ..mixins import StudyMixin
from ..models import Resource
from ..models import Study
from ..models import StudySession


class StudySessionsView(StudyMixin, PermissionRequiredMixin, UpdateView):
    model = Study
    pk_url_kwarg = 'study_pk'
    template_name = 'studies/study_sessions.html'
    fields = [
        'session_instructions',
        'sessions_start',
        'sessions_end',
    ]
    permission_required = 'studies.change_study'
    is_onetime_invitation = False
    tab = 'sessions'

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('studies:sessions', args=[self.object.pk])


class StudySessionFormMixin(StudyMixin, PermissionRequiredMixin):
    model = StudySession
    form_class = SessionForm
    permission_required = 'studies.change_study'
    is_onetime_invitation = False
    tab = 'sessions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_resources'] = Resource.objects.exists()
        if settings.SCHEDULER_URL and self.object:
            context['schedule_url'] = scheduler.get_schedule_url(self.object.schedule_id)
        return context

    def get_success_url(self):
        return reverse('studies:sessions', args=[self.study.pk])


class StudySessionCreateView(StudySessionFormMixin, CreateView):
    def form_valid(self, form):
        form.instance.study = self.study
        return super().form_valid(form)


class StudySessionUpdateView(StudySessionFormMixin, UpdateView):
    def get_object(self):
        return get_object_or_404(
            StudySession, pk=self.kwargs['pk'], study_id=self.kwargs['study_pk']
        )


class StudySessionDeleteView(StudyMixin, PermissionRequiredMixin, DeleteView):
    model = StudySession
    permission_required = 'studies.change_study'
    is_onetime_invitation = False
    tab = 'sessions'

    def get_success_url(self):
        return reverse('studies:sessions', args=[self.study.pk])

    def get_object(self):
        return get_object_or_404(
            StudySession, pk=self.kwargs['pk'], study_id=self.kwargs['study_pk']
        )


class StudyReminderTestMailView(StudyMixin, PermissionRequiredMixin, View):
    model = StudySession
    permission_required = 'studies.change_study'

    def get_object(self):
        return get_object_or_404(
            StudySession, pk=self.kwargs['pk'], study_id=self.kwargs['study_pk']
        )

    def post(self, request, **kwargs):
        self.object = self.get_object()

        with MailContext('recruitment') as ctx:
            name = request.user.get_full_name() or request.user.username
            success = ctx.send_mail(
                settings.CASTELLUM_APPOINTMENT_MAIL_SUBJECT,
                get_reminder_body(name, self.object, timezone.now()),
                [request.user.email],
                reply_to=[self.study.email],
            )

        if success:
            messages.success(self.request, _('Test mail has been sent.'))
        else:
            messages.error(self.request, _('Could not send test mail.'))

        return redirect('studies:session-update', self.study.pk, self.object.pk)
