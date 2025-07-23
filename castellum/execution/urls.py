# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.urls import path

from .api import APIAttributesView
from .api import APIDomainsView
from .api import APIPseudonymsView
from .api import APIResolveView
from .api import APIValidateView
from .feeds import AppointmentFeedForUser
from .views import AdditionalInfoUpdateView
from .views import AttributesUpdateView
from .views import CalendarView
from .views import ConsentChangeView
from .views import ContactUpdateView
from .views import DataProtectionUpdateView
from .views import ExclusionCriteriaView
from .views import ExportView
from .views import LegalRepresentativeContactUpdateView
from .views import NewsMailView
from .views import ParticipationAppointmentsUpdateView
from .views import ParticipationConsentCreateView
from .views import ParticipationConsentDeleteView
from .views import ParticipationConsentView
from .views import ParticipationDetailView
from .views import ParticipationDropoutConfirmView
from .views import ParticipationListView
from .views import ParticipationPseudonymsView
from .views import ParticipationPseudonymView
from .views import ParticipationStatusView
from .views import ParticipationUpdateView
from .views import ProgressView
from .views import RelationCreateView
from .views import RelationDeleteView
from .views import ReportView
from .views import ResolveView
from .views import TagView

app_name = 'execution'
urlpatterns = [
    path('calendar/feed/', AppointmentFeedForUser.as_view(), name='calendar-user-feed'),
    path('<int:study_pk>/', ParticipationListView.as_view(), name='participation-list'),
    path('<int:study_pk>/resolve/', ResolveView.as_view(), name='resolve'),
    path('<int:study_pk>/news/', NewsMailView.as_view(), name='news-mail'),
    path('<int:pk>/calendar/', CalendarView.as_view(), name='calendar'),
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
        '<int:study_pk>/<int:pk>/status/',
        ParticipationStatusView.as_view(),
        name='participation-status',
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
        '<int:study_pk>/<int:pk>/consent/',
        ParticipationConsentView.as_view(),
        name='participation-consent',
    ),
    path(
        '<int:study_pk>/<int:pk>/consent/add/',
        ParticipationConsentCreateView.as_view(),
        name='participation-consent-create',
    ),
    path(
        '<int:study_pk>/<int:participation_pk>/consent/<int:pk>/delete/',
        ParticipationConsentDeleteView.as_view(),
        name='participation-consent-delete',
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
        '<int:study_pk>/<int:pk>/update-attributes/',
        AttributesUpdateView.as_view(),
        name='attributes-update',
    ),
    path(
        '<int:study_pk>/<int:pk>/relations/create/',
        RelationCreateView.as_view(),
        name='relation-create',
    ),
    path(
        '<int:study_pk>/<int:participation_pk>/relations/<int:pk>/delete/',
        RelationDeleteView.as_view(),
        name='relation-delete',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-data-protection/',
        DataProtectionUpdateView.as_view(),
        name='data-protection-update',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-data-protection/consent/',
        ConsentChangeView.as_view(),
        name='consent-change',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-additional-info/',
        AdditionalInfoUpdateView.as_view(),
        name='additional-info-update',
    ),
    path(
        '<int:study_pk>/<int:participation_pk>/representatives/<hash>/update-contact/',
        LegalRepresentativeContactUpdateView.as_view(),
        name='legal-representative-contact-update',
    ),
    path('<int:study_pk>/<int:pk>/report/', ReportView.as_view(), name='report'),
]

if settings.CASTELLUM_API_ENABLED:
    urlpatterns += [
        path('api/studies/<int:pk>/domains/', APIDomainsView.as_view()),
        path(
            'api/studies/<int:pk>/domains/<uuid:domain>/', APIPseudonymsView.as_view()
        ),
        path(
            'api/studies/<int:pk>/domains/<uuid:domain>/<pseudonym>/',
            APIValidateView.as_view(),
        ),
        path(
            'api/studies/<int:study_pk>/domains/<uuid:domain>/<pseudonym>/attributes/',
            APIAttributesView.as_view(),
        ),
        path(
            'api/studies/<int:study_pk>/domains/<uuid:domain>/<pseudonym>/<uuid:target_domain>/',
            APIResolveView.as_view(),
        ),
    ]
