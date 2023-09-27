# (c) 2018-2023 MPIB <https://www.mpib-berlin.mpg.de/>,
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
from django.urls import include
from django.urls import path

from ..views.api import APIStudyDetailView
from ..views.api import APIStudyListView
from ..views.studies import FilterTrialCreateView
from ..views.studies import StudyConsentView
from ..views.studies import StudyCreateView
from ..views.studies import StudyDeleteView
from ..views.studies import StudyDetailView
from ..views.studies import StudyDomainDeleteView
from ..views.studies import StudyDomainsGeneralView
from ..views.studies import StudyDomainsView
from ..views.studies import StudyFinishRecruitmentView
from ..views.studies import StudyIndexView
from ..views.studies import StudyMaintenanceView
from ..views.studies import StudyStartRecruitmentView
from ..views.studies import StudyUpdateView
from . import members as members_urls
from . import recruitment as recruitment_urls
from . import sessions as sessions_urls

app_name = 'studies'
urlpatterns = [
    path('', StudyIndexView.as_view(), name='index'),
    path('maintenance/<subtab>/', StudyMaintenanceView.as_view(), name='maintenance'),
    path('create/', StudyCreateView.as_view(), name='create'),
    path(
        'create/filtertrial/',
        FilterTrialCreateView.as_view(),
        name='create-filter-trial',
    ),
    path('<int:pk>/', StudyDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', StudyUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', StudyDeleteView.as_view(), name='delete'),
    path('<int:pk>/domains/', StudyDomainsView.as_view(), name='domains'),
    path(
        '<int:pk>/domains/general/',
        StudyDomainsGeneralView.as_view(),
        name='domains-general',
    ),
    path('<int:pk>/consent/', StudyConsentView.as_view(), name='consent'),
    path(
        '<int:study_pk>/domains/<uuid:key>/',
        StudyDomainDeleteView.as_view(),
        name='domain-delete',
    ),
    path('<int:study_pk>/start/', StudyStartRecruitmentView.as_view(), name='start'),
    path('<int:study_pk>/finish/', StudyFinishRecruitmentView.as_view(), name='finish'),
    path('<int:study_pk>/members/', include(members_urls)),
    path('<int:study_pk>/recruitmentsettings/', include(recruitment_urls)),
    path('<int:study_pk>/sessions/', include(sessions_urls)),
]
if settings.CASTELLUM_API_ENABLED:
    urlpatterns += [
        path('api/studies/', APIStudyListView.as_view()),
        path('api/studies/<int:pk>/', APIStudyDetailView.as_view()),
    ]
