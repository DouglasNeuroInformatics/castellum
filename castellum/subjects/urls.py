# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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
from .views import AdditionalInfoUpdateView
from .views import AttributesUpdateView
from .views import ContactUpdateView
from .views import CoverletterView
from .views import DataProtectionUpdateView
from .views import LegalRepresentativeSearchView
from .views import MaintenanceAttributesView
from .views import MaintenanceConsentView
from .views import MaintenanceContactView
from .views import MaintenanceDuplicatesView
from .views import MaintenanceEstrangedSubjectsView
from .views import MaintenanceNotesView
from .views import MaintenanceReliabilityView
from .views import MaintenanceSubjectCreationRequestView
from .views import MaintenanceWaitingView
from .views import ParticipationAddView
from .views import ParticipationDeleteView
from .views import ParticipationListView
from .views import ParticipationRecruitView
from .views import SubjectCreationRequestDeleteView
from .views import SubjectDeleteView
from .views import SubjectDetailView
from .views import SubjectExportView
from .views import SubjectPseudonymsView
from .views import SubjectPseudonymView
from .views import SubjectSearchView

app_name = 'subjects'
urlpatterns = [
    path('', SubjectSearchView.as_view(), name='index'),
    path(
        'representatives/',
        LegalRepresentativeSearchView.as_view(),
        name='legal-representative-search',
    ),
    path(
        'maintenance/attributes/',
        MaintenanceAttributesView.as_view(),
        name='maintenance-attributes',
    ),
    path('maintenance/contact/', MaintenanceContactView.as_view(), name='maintenance-contact'),
    path('maintenance/consent/', MaintenanceConsentView.as_view(), name='maintenance-consent'),
    path(
        'maintenance/duplicates/',
        MaintenanceDuplicatesView.as_view(),
        name='maintenance-duplicates',
    ),
    path('maintenance/waiting/', MaintenanceWaitingView.as_view(), name='maintenance-waiting'),
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
    path('maintenance/notes/', MaintenanceNotesView.as_view(), name='maintenance-notes'),
    path('<uuid:uuid>/', SubjectDetailView.as_view(), name='detail'),
    path('<uuid:uuid>/pseudonyms/', SubjectPseudonymsView.as_view(), name='pseudonyms'),
    path('<uuid:uuid>/pseudonyms/<domain>/', SubjectPseudonymView.as_view(), name='pseudonym'),
    path('<uuid:uuid>/delete/', SubjectDeleteView.as_view(), name='delete'),
    path('<uuid:uuid>/export/', SubjectExportView.as_view(), name='export'),
    path('<uuid:uuid>/contact/', ContactUpdateView.as_view(), name='contact'),
    path('<uuid:uuid>/attributes/', AttributesUpdateView.as_view(), name='attributes'),
    path(
        '<uuid:uuid>/data-protection/',
        DataProtectionUpdateView.as_view(),
        name='data-protection',
    ),
    path(
        '<uuid:uuid>/additional-info/',
        AdditionalInfoUpdateView.as_view(),
        name='additional-info',
    ),
    path(
        '<uuid:uuid>/coverletter.docx',
        CoverletterView.as_view(),
        name='coverletter',
    ),
    path('<uuid:uuid>/participations/', ParticipationListView.as_view(), name='participation-list'),
    path(
        '<uuid:uuid>/participations/recruit/',
        ParticipationRecruitView.as_view(),
        name='participation-recruit',
    ),
    path(
        '<uuid:uuid>/participations/add/',
        ParticipationAddView.as_view(),
        name='participation-add',
    ),
    path(
        '<uuid:subject_uuid>/participations/<int:pk>/delete/',
        ParticipationDeleteView.as_view(),
        name='participation-delete',
    ),
]

if settings.CASTELLUM_API_ENABLED:
    urlpatterns += [
        path('api/subjects/<uuid:domain>/<pseudonym>/attributes/', APIAttributesView.as_view()),
    ]
