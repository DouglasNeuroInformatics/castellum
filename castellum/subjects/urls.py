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

from django.urls import path

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
from .views import MaintenanceNotesView
from .views import MaintenanceReliabilityView
from .views import MaintenanceSubjectCreationRequestDeleteView
from .views import MaintenanceSubjectCreationRequestView
from .views import MaintenanceWaitingView
from .views import ParticipationAddView
from .views import ParticipationDeleteView
from .views import ParticipationListView
from .views import ParticipationRecruitView
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
        'maintenance/subjectcreationrequest/',
        MaintenanceSubjectCreationRequestView.as_view(),
        name='maintenance-subjectcreationrequest',
    ),
    path(
        'maintenance/subjectcreationrequest/<int:pk>/delete/',
        MaintenanceSubjectCreationRequestDeleteView.as_view(),
        name='maintenance-subjectcreationrequest-delete',
    ),
    path('maintenance/notes/', MaintenanceNotesView.as_view(), name='maintenance-notes'),
    path('<uuid>/', SubjectDetailView.as_view(), name='detail'),
    path('<uuid>/pseudonyms/', SubjectPseudonymsView.as_view(), name='pseudonyms'),
    path('<uuid>/pseudonyms/<domain>/', SubjectPseudonymView.as_view(), name='pseudonym'),
    path('<uuid>/delete/', SubjectDeleteView.as_view(), name='delete'),
    path('<uuid>/export/', SubjectExportView.as_view(), name='export'),
    path('<uuid>/contact/', ContactUpdateView.as_view(), name='contact'),
    path('<uuid>/attributes/', AttributesUpdateView.as_view(), name='attributes'),
    path('<uuid>/data-protection/', DataProtectionUpdateView.as_view(), name='data-protection'),
    path('<uuid>/additional-info/', AdditionalInfoUpdateView.as_view(), name='additional-info'),
    path('<uuid>/coverletter.docx', CoverletterView.as_view(), name='coverletter'),
    path('<uuid>/participations/', ParticipationListView.as_view(), name='participation-list'),
    path(
        '<uuid>/participations/recruit/',
        ParticipationRecruitView.as_view(),
        name='participation-recruit',
    ),
    path('<uuid>/participations/add/', ParticipationAddView.as_view(), name='participation-add'),
    path(
        '<subject_uuid>/participations/<int:pk>/delete/',
        ParticipationDeleteView.as_view(),
        name='participation-delete',
    ),
]
