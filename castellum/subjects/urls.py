# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.urls import path

from .api import APIAttributesView
from .views import AdditionalInfoUpdateView
from .views import AttributesUpdateView
from .views import ConsentChangeView
from .views import ContactUpdateView
from .views import DataProtectionUpdateView
from .views import DeleteRecruitmentDataView
from .views import MaintenanceAttributesView
from .views import MaintenanceConsentView
from .views import MaintenanceContactView
from .views import MaintenanceDuplicatesView
from .views import MaintenanceEstrangedSubjectsView
from .views import MaintenanceReliabilityView
from .views import MaintenanceSubjectCreationRequestView
from .views import ParticipationAddView
from .views import ParticipationDeleteView
from .views import ParticipationListView
from .views import ParticipationRecruitView
from .views import ReportDetailView
from .views import ReportView
from .views import SubjectAuditTrailView
from .views import SubjectCreationRequestDeleteView
from .views import SubjectDeleteView
from .views import SubjectDetailView
from .views import SubjectExportView
from .views import SubjectPseudonymsView
from .views import SubjectPseudonymView
from .views import SubjectResolveView
from .views import SubjectSearchPopup
from .views import SubjectSearchView

app_name = 'subjects'
urlpatterns = [
    path('', SubjectSearchView.as_view(), name='index'),
    path('resolve/', SubjectResolveView.as_view(), name='resolve'),
    path(
        'search-popup/',
        SubjectSearchPopup.as_view(),
        name='subject-search-popup',
    ),
    path(
        'maintenance/attributes/',
        MaintenanceAttributesView.as_view(),
        name='maintenance-attributes',
    ),
    path(
        'maintenance/contact/',
        MaintenanceContactView.as_view(),
        name='maintenance-contact',
    ),
    path(
        'maintenance/consent/',
        MaintenanceConsentView.as_view(),
        name='maintenance-consent',
    ),
    path(
        'maintenance/duplicates/',
        MaintenanceDuplicatesView.as_view(),
        name='maintenance-duplicates',
    ),
    path(
        'maintenance/reliability/',
        MaintenanceReliabilityView.as_view(),
        name='maintenance-reliability',
    ),
    path(
        'maintenance/estranged-subjects/',
        MaintenanceEstrangedSubjectsView.as_view(),
        name='maintenance-estranged-subjects',
    ),
    path(
        'maintenance/subjectcreationrequest/',
        MaintenanceSubjectCreationRequestView.as_view(),
        name='maintenance-subjectcreationrequest',
    ),
    path(
        'subjectcreationrequest/<int:pk>/delete/',
        SubjectCreationRequestDeleteView.as_view(),
        name='maintenance-subjectcreationrequest-delete',
    ),
    path('<uuid:pk>/', SubjectDetailView.as_view(), name='detail'),
    path('<uuid:pk>/pseudonyms/', SubjectPseudonymsView.as_view(), name='pseudonyms'),
    path(
        '<uuid:pk>/pseudonyms/<domain>/',
        SubjectPseudonymView.as_view(),
        name='pseudonym',
    ),
    path('<uuid:pk>/delete/', SubjectDeleteView.as_view(), name='delete'),
    path('<uuid:pk>/export/', SubjectExportView.as_view(), name='export'),
    path('<uuid:pk>/contact/', ContactUpdateView.as_view(), name='contact'),
    path('<uuid:pk>/attributes/', AttributesUpdateView.as_view(), name='attributes'),
    path(
        '<uuid:pk>/attributes/delete/',
        DeleteRecruitmentDataView.as_view(),
        name='delete-recruitment-data',
    ),
    path(
        '<uuid:pk>/data-protection/',
        DataProtectionUpdateView.as_view(),
        name='data-protection',
    ),
    path(
        '<uuid:pk>/data-protection/consent/',
        ConsentChangeView.as_view(),
        name='consent',
    ),
    path(
        '<uuid:pk>/additional-info/',
        AdditionalInfoUpdateView.as_view(),
        name='additional-info',
    ),
    path(
        '<uuid:pk>/participations/',
        ParticipationListView.as_view(),
        name='participation-list',
    ),
    path(
        '<uuid:pk>/participations/recruit/',
        ParticipationRecruitView.as_view(),
        name='participation-recruit',
    ),
    path(
        '<uuid:pk>/participations/add/',
        ParticipationAddView.as_view(),
        name='participation-add',
    ),
    path(
        '<uuid:subject_pk>/participations/<int:pk>/delete/',
        ParticipationDeleteView.as_view(),
        name='participation-delete',
    ),
    path('<uuid:pk>/report/', ReportView.as_view(), name='report'),
    path('reports/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
]

if settings.CASTELLUM_AUDIT_TRAIL_ENABLED:
    urlpatterns += [
        path(
            '<uuid:pk>/audit-trail/',
            SubjectAuditTrailView.as_view(),
            name='audit-trail',
        ),
    ]

if settings.CASTELLUM_API_ENABLED:
    urlpatterns += [
        path(
            'api/subjects/<uuid:domain>/<pseudonym>/attributes/',
            APIAttributesView.as_view(),
        ),
    ]
