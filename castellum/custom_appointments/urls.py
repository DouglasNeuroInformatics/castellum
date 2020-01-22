from django.urls import path


from .views import MembershipsView

# from .views import AppointmentsView
# from .views import CreateAppointmentView
# from .views import UpdateAppointmentView
# from .views import RemoveAppointmentView
# from .views import AddParticipantsView
# from .views import AcceptAppointmentView
# from .views import DeclineAppointmentView
# from .views import RemoveParticipantsView

app_name = 'custom_appointments'

urlpatterns = [
    path('memberships/', MembershipsView.as_view(), name='memberships'),

    # path('appointments/', AppointmentsView.as_view(), name='appointments'),
    # path('appointments/create/', CreateAppointmentView.as_view(), name='create_appointment'),
    # path('appointments/update/<appointment_id>/', UpdateAppointmentView.as_view(), name='change_appointment'),
    # path('appointments/remove/<appointment_id>/', RemoveAppointmentView.as_view(), name='remove_appointment'),
    #
    # path('appointments/<appointment_id>/add/', AddParticipantsView.as_view(), name='add_participants'),
    # path('appointments/<appointment_id>/remove/', RemoveParticipantsView.as_view(), name='remove_participants'),
    # path('appointments/<appointment_id>/accept/', AcceptAppointmentView.as_view(), name='accept_appointment'),
    # path('appointments/<appointment_id>/decline/', DeclineAppointmentView.as_view(), name='decline_appointment'),


]
