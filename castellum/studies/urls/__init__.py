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

from django.conf import settings
from django.urls import include
from django.urls import path

from ..views.recruitment import OneTimeInvitationMailRecruitmentView
from ..views.studies import StudyCreateView
from ..views.studies import StudyDeleteView
from ..views.studies import StudyDetailView
from ..views.studies import StudyExportView
from ..views.studies import StudyFinishRecruitmentView
from ..views.studies import StudyImportView
from ..views.studies import StudyIndexView
from ..views.studies import StudyStartRecruitmentView
from ..views.studies import StudyUpdateView
from . import members as members_urls
from . import recruitment as recruitment_urls

app_name = 'studies'
urlpatterns = [
    path('', StudyIndexView.as_view(), name='index'),
    path('create/', StudyCreateView.as_view(), name='create'),
    path('<int:pk>/', StudyDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', StudyUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', StudyDeleteView.as_view(), name='delete'),
    path('<int:study_pk>/start/', StudyStartRecruitmentView.as_view(), name='start'),
    path(
        '<int:study_pk>/finish-recruitment/',
        StudyFinishRecruitmentView.as_view(),
        name='finish-recruitment',
    ),
    path('<int:pk>/mail/', OneTimeInvitationMailRecruitmentView.as_view(), name='mail'),
    path('<int:study_pk>/members/', include(members_urls)),
    path('<int:study_pk>/recruitmentsettings/', include(recruitment_urls)),
]

if settings.CASTELLUM_ENABLE_STUDY_EXPORT:
    urlpatterns += [
        path('import/', StudyImportView.as_view(), name='import'),
        path('<int:pk>/export/', StudyExportView.as_view(), name='export'),
    ]
