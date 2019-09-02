import datetime

from django.views.generic import TemplateView
from django.views.generic import RedirectView
from django.urls import reverse
from appointments.services import get_appointments
from appointments.services import create_appointment
from appointments.services import update_appointment
from appointments.services import remove_appointment
from appointments.services import accept_appointment
from appointments.services import decline_appointment
from appointments.services import get_invitations
from appointments.services import add_participants
from appointments.services import remove_participants


class BasicRedirect(RedirectView):
    permanent = False
    query_string = True

class InvitationsView(TemplateView):

    template_name = 'custom_appointments/invitations.html'

    def get_context_data(self, **kwargs):

        context = super(InvitationsView, self).get_context_data(**kwargs)
        context['invitations'] = get_invitations()
        return context


class AddParticipantsView(BasicRedirect):

    def get_redirect_url(self, *args, **kwargs):
        appointment_id = kwargs.get('appointment_id')

        participants = []
        if self.request.GET.get('participants'):
            participants = self.request.GET.get('participants').split(',')

        if appointment_id and participants:
            add_participants(
                appointment_id=appointment_id,
                participants=participants
            )
        return reverse('custom_appointments:invitations')


class RemoveParticipantsView(BasicRedirect):

    def get_redirect_url(self, *args, **kwargs):
        appointment_id = kwargs.get('appointment_id')

        participants = []
        if self.request.GET.get('participants'):
            participants = self.request.GET.get('participants').split(',')

        if appointment_id and participants:
            remove_participants(
                appointment_id=appointment_id,
                participants=participants
            )
        return reverse('custom_appointments:invitations')


class AcceptAppointmentView(BasicRedirect):

    def get_redirect_url(self, *args, **kwargs):
        appointment_id = kwargs.get('appointment_id')

        participant = self.request.GET.get('participant')

        if appointment_id and participant:
            accept_appointment(
                appointment_id=appointment_id,
                participant=participant,
            )
        return reverse('custom_appointments:invitations')


class DeclineAppointmentView(BasicRedirect):

    def get_redirect_url(self, *args, **kwargs):
        appointment_id = kwargs.get('appointment_id')

        participant = self.request.GET.get('participant')

        if appointment_id and participant:
            decline_appointment(
                appointment_id=appointment_id,
                participant=participant,
            )
        return reverse('custom_appointments:invitations')


class AppointmentsView(TemplateView):

    template_name = 'custom_appointments/appointments.html'

    def get_context_data(self, **kwargs):

        data = {}
        # it is possible to use any model fields for sorting, not only start_min and end_max
        if self.request.GET.get('start_min'):
            data['start_min'] = datetime.datetime.strptime(self.request.GET.get('start_min'), "%d%m%Y").date()

        if self.request.GET.get('end_max'):
            data['end_max'] = datetime.datetime.strptime(self.request.GET.get('end_max'), "%d%m%Y").date()

        print(data)
        context = super(AppointmentsView, self).get_context_data(**kwargs)
        context['appointments'] = get_appointments(data)

        return context


class CreateAppointmentView(BasicRedirect):

    def get_redirect_url(self, *args, **kwargs):
        participants = []
        if self.request.GET.get('participants'):
            participants = self.request.GET.get('participants').split(',')

        creator = self.request.GET.get('creator', 'DefaultCreator')
        location = self.request.GET.get('location', 'DefaultLocation')

        if self.request.GET.get('start'):
            start = datetime.datetime.strptime(self.request.GET.get('start'), "%d%m%Y %H:%M")
        else:
            start = datetime.datetime.now()

        if self.request.GET.get('end'):
            end = datetime.datetime.strptime(self.request.GET.get('end'), "%d%m%Y %H:%M")
        else:
            end = datetime.datetime.now()

        create_appointment(
                creator=creator,
                location=location,
                start=start,
                end=end,
                participants=participants
        )
        return reverse('custom_appointments:appointments')


class UpdateAppointmentView(BasicRedirect):

    def get_redirect_url(self, *args, **kwargs):
        appointment_id = kwargs.get('appointment_id')

        location = 'NiceLocation'
        if self.request.GET.get('location'):
            location = self.request.GET.get('location')

        start = datetime.datetime(2019, 8, 5, 8, 0)
        end = datetime.datetime(2019, 8, 7, 9, 0)

        if appointment_id:
            update_appointment(
                appointment_id=appointment_id,
                location=location,
                start=start,
                end=end
            )
        return reverse('custom_appointments:appointments')


class RemoveAppointmentView(BasicRedirect):

    def get_redirect_url(self, *args, **kwargs):
        appointment_id = kwargs.get('appointment_id')
        if appointment_id:
            remove_appointment(appointment_id)
        return reverse('custom_appointments:appointments')

