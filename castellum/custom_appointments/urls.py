from django.urls import path

from .views import AppointmentsView

app_name = 'custom_appointments'

urlpatterns = [
    path('', AppointmentsView.as_view(), name='appointments'),
]
