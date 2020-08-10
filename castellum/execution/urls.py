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

from django.urls import path

from .feeds import AppointmentFeed
from .views import AdditionalInfoUpdateView
from .views import AttributeSetUpdateView
from .views import CalendarView
from .views import ContactUpdateView
from .views import DataProtectionUpdateView
from .views import ParticipationAppointmentsView
from .views import ParticipationCriteriaView
from .views import ParticipationDetailView
from .views import ParticipationOutcomeView
from .views import ReceptionView
from .views import ResolveView
from .views import ShowUpUpdateView
from .views import StudyDetailView

app_name = 'execution'
urlpatterns = [
    path('reception/', ReceptionView.as_view(), name='reception'),
    path('<int:study_pk>/', StudyDetailView.as_view(), name='study-detail'),
    path('<int:study_pk>/resolve/', ResolveView.as_view(), name='resolve'),
    path('<int:pk>/calendar/', CalendarView.as_view(), name='calendar'),
    path('<int:pk>/calendar/feed/', AppointmentFeed(), name='calendar-feed'),
    path(
        '<int:study_pk>/<int:pk>/',
        ParticipationDetailView.as_view(),
        name='participation-detail',
    ),
    path(
        '<int:study_pk>/<int:pk>/outcome/',
        ParticipationOutcomeView.as_view(),
        name='participation-outcome',
    ),
    path(
        '<int:study_pk>/<int:pk>/criteria/',
        ParticipationCriteriaView.as_view(),
        name='participation-criteria',
    ),
    path(
        '<int:study_pk>/<int:pk>/appointments/',
        ParticipationAppointmentsView.as_view(),
        name='participation-appointments',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-contact/',
        ContactUpdateView.as_view(),
        name='contact-update',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-attributeset/',
        AttributeSetUpdateView.as_view(),
        name='attributeset-update',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-data-protection/',
        DataProtectionUpdateView.as_view(),
        name='data-protection-update',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-additional-info/',
        AdditionalInfoUpdateView.as_view(),
        name='additional-info-update',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-show-up/<int:appointment_pk>',
        ShowUpUpdateView.as_view(),
        name='show-up',
    ),
]
