from django.views.generic import TemplateView
from appointments.services import get_appointments

class AppointmentsView(TemplateView):

    template_name = 'custom_appointments/appointments.html'

    def get_context_data(self, **kwargs):

        context = super(AppointmentsView, self).get_context_data(**kwargs)
        context['appointments'] = get_appointments()
        print(context['appointments'])
        return context

