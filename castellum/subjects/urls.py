# (c) 2018
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

from .views import AddToStudyView
from .views import AttributeSetUpdateView
from .views import ContactUpdateView
from .views import CoverletterView
from .views import GuardianSearchView
from .views import MaintenanceAttributesView
from .views import MaintenanceConsentView
from .views import MaintenanceContactView
from .views import ParticipationDeleteView
from .views import ParticipationListView
from .views import SubjectDeleteView
from .views import SubjectDetailView
from .views import SubjectExportView
from .views import SubjectSearchView
from .views import SubjectUpdateView

app_name = 'subjects'
urlpatterns = [
    path('', SubjectSearchView.as_view(), name='index'),
    path('<int:pk>/', SubjectDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', SubjectDeleteView.as_view(), name='delete'),
    path('<int:pk>/export/', SubjectExportView.as_view(), name='export'),
    path('<int:pk>/subject/', SubjectUpdateView.as_view(), name='subject'),
    path('<int:pk>/contact/', ContactUpdateView.as_view(), name='contact'),
    path('<int:pk>/attributes/', AttributeSetUpdateView.as_view(), name='attributeset'),
    path('<int:pk>/coverletter.docx', CoverletterView.as_view(), name='coverletter'),
    path(
        '<int:pk>/studyparticipation/',
        ParticipationListView.as_view(),
        name='studyparticipation',
    ),
    path('<int:pk>/studyparticipation/add/', AddToStudyView.as_view(), name='add-to-study'),
    path(
        '<int:subject_pk>/studyparticipation/<int:pk>/delete/',
        ParticipationDeleteView.as_view(),
        name='studyparticipation-delete',
    ),
    path('guardians/', GuardianSearchView.as_view(), name='guardian-search'),
    path(
        'maintenance/attributes/',
        MaintenanceAttributesView.as_view(),
        name='maintenance-attributes',
    ),
    path('maintenance/contact/', MaintenanceContactView.as_view(), name='maintenance-contact'),
    path('maintenance/consent/', MaintenanceConsentView.as_view(), name='maintenance-consent'),
]
