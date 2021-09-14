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
from django.urls import path

from .api import APIAttributesView
from .api import APIDomainsView
from .api import APIPseudonymsView
from .api import APIResolveView
from .api import APIValidateView
from .feeds import AppointmentFeedForStudy
from .feeds import AppointmentFeedForUser
from .views import AdditionalInfoUpdateView
from .views import AttributesUpdateView
from .views import CalendarView
from .views import ContactUpdateView
from .views import DataProtectionUpdateView
from .views import ExclusionCriteriaView
from .views import ExportView
from .views import GuardianContactUpdateView
from .views import NewsMailView
from .views import ParticipationAppointmentsUpdateView
from .views import ParticipationDetailView
from .views import ParticipationDropoutConfirmView
from .views import ParticipationDropoutView
from .views import ParticipationPseudonymsView
from .views import ParticipationPseudonymView
from .views import ParticipationUpdateView
from .views import ProgressView
from .views import ResolveView
from .views import StudyDetailView
from .views import TagView

app_name = 'execution'
urlpatterns = [
    path('calendar/feed/', AppointmentFeedForUser(), name='calendar-user-feed'),
    path('<int:study_pk>/', StudyDetailView.as_view(), name='study-detail'),
    path('<int:study_pk>/resolve/', ResolveView.as_view(), name='resolve'),
    path('<int:study_pk>/news/', NewsMailView.as_view(), name='news-mail'),
    path('<int:pk>/calendar/', CalendarView.as_view(), name='calendar'),
    path('<int:pk>/calendar/feed/', AppointmentFeedForStudy(), name='calendar-feed'),
    path('<int:pk>/criteria/', ExclusionCriteriaView.as_view(), name='criteria'),
    path('<int:pk>/export/', ExportView.as_view(), name='export'),
    path('<int:pk>/progress/', ProgressView.as_view(), name='progress'),
    path('<int:pk>/tags/', TagView.as_view(), name='execution-tags'),
    path(
        '<int:study_pk>/<int:pk>/',
        ParticipationDetailView.as_view(),
        name='participation-detail',
    ),
    path(
        '<int:study_pk>/<int:pk>/pseudonyms/',
        ParticipationPseudonymsView.as_view(),
        name='participation-pseudonyms',
    ),
    path(
        '<int:study_pk>/<int:pk>/pseudonyms/<domain>/',
        ParticipationPseudonymView.as_view(),
        name='participation-pseudonym',
    ),
    path(
        '<int:study_pk>/<int:pk>/dropout/',
        ParticipationDropoutView.as_view(),
        name='participation-dropout',
    ),
    path(
        '<int:study_pk>/<int:pk>/dropout/confirm/',
        ParticipationDropoutConfirmView.as_view(),
        name='participation-dropout-confirm',
    ),
    path(
        '<int:study_pk>/<int:pk>/update/',
        ParticipationUpdateView.as_view(),
        name='participation-update',
    ),
    path(
        '<int:study_pk>/<int:pk>/appointments/',
        ParticipationAppointmentsUpdateView.as_view(),
        name='participation-appointments',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-contact/',
        ContactUpdateView.as_view(),
        name='contact-update',
    ),
    path(
        # FIXME: no study-local way to identify guardian
        # PK is leaked in HTML, so we can use that
        '<int:study_pk>/<int:pk>/guardian-update-contact/<int:guardian_pk>/',
        GuardianContactUpdateView.as_view(),
        name='guardian-contact-update',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-attributes/',
        AttributesUpdateView.as_view(),
        name='attributes-update',
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
]

if settings.CASTELLUM_PSEUDONYMS_API_ENABLED:
    urlpatterns += [
        path('<int:pk>/api/domains/', APIDomainsView.as_view()),
        path('<int:pk>/api/domains/<uuid:domain>/', APIPseudonymsView.as_view()),
        path('<int:pk>/api/domains/<uuid:domain>/<pseudonym>/', APIValidateView.as_view()),
        path(
            '<int:study_pk>/api/domains/<uuid:domain>/<pseudonym>/attributes/',
            APIAttributesView.as_view()
        ),
        path(
            '<int:study_pk>/api/domains/<uuid:domain>/<pseudonym>/<uuid:target_domain>/',
            APIResolveView.as_view()
        ),
    ]
