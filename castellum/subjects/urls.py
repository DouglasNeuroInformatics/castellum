# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.urls import path

from .views.api import APIAttributesView
from .views.blocklist import BlockListFileView
from .views.blocklist import BlockListFormView
from .views.maintenance import MaintenanceAttributesView
from .views.maintenance import MaintenanceConsentView
from .views.maintenance import MaintenanceDuplicatesView
from .views.maintenance import MaintenanceEstrangedSubjectsView
from .views.maintenance import MaintenanceReliabilityView
from .views.maintenance import MaintenanceSubjectCreationRequestView
from .views.maintenance import SubjectCreationRequestDeleteView
from .views.participation import ParticipationAddView
from .views.participation import ParticipationDeleteView
from .views.participation import ParticipationListView
from .views.participation import ParticipationRecruitView
from .views.subject import AdditionalInfoUpdateView
from .views.subject import AttributesUpdateView
from .views.subject import ConsentChangeView
from .views.subject import ContactUpdateView
from .views.subject import DataProtectionUpdateView
from .views.subject import DeleteRecruitmentDataView
from .views.subject import RelationCreateView
from .views.subject import RelationDeleteView
from .views.subject import ReportDetailView
from .views.subject import ReportView
from .views.subject import SubjectAuditTrailView
from .views.subject import SubjectDeleteView
from .views.subject import SubjectDetailView
from .views.subject import SubjectExportView
from .views.subject import SubjectMergeView
from .views.subject import SubjectPseudonymsView
from .views.subject import SubjectPseudonymView
from .views.subject import SubjectResolveView
from .views.subject import SubjectSearchPopup
from .views.subject import SubjectSearchView

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
    path('blocklist/', BlockListFormView.as_view(), name='blocklist'),
    path('blocklist/batch/', BlockListFileView.as_view(), name='blocklist-batch'),
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
    path('<uuid:pk>/merge/', SubjectMergeView.as_view(), name='merge'),
    path('<uuid:pk>/export/', SubjectExportView.as_view(), name='export'),
    path('<uuid:pk>/contact/', ContactUpdateView.as_view(), name='contact'),
    path('<uuid:pk>/attributes/', AttributesUpdateView.as_view(), name='attributes'),
    path(
        '<uuid:pk>/attributes/delete/',
        DeleteRecruitmentDataView.as_view(),
        name='delete-recruitment-data',
    ),
    path(
        '<uuid:subject_uuid>/relations/create/',
        RelationCreateView.as_view(),
        name='relation-create',
    ),
    path(
        '<uuid:subject_uuid>/relations/<int:pk>/delete/',
        RelationDeleteView.as_view(),
        name='relation-delete',
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
