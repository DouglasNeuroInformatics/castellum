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

from .views import StudyCreateView
from .views import StudyExclusionCriteriaView
from .views import StudyIndexView
from .views import StudyMemberRemoveView
from .views import StudyMembersView
from .views import StudyMemberUpdateView
from .views import StudyPublishView
from .views import StudyRecruitmentSettingsView
from .views import StudyUpdateView

app_name = 'studies'
urlpatterns = [
    path('', StudyIndexView.as_view(), name='index'),
    path('create/', StudyCreateView.as_view(), name='create'),
    path('<int:pk>/update/', StudyUpdateView.as_view(), name='update'),
    path('<int:study_pk>/publish/', StudyPublishView.as_view(), name='publish'),
    path('<int:pk>/members/', StudyMembersView.as_view(), name='members'),
    path('<int:study_pk>/members/<int:pk>/', StudyMemberUpdateView.as_view(), name='member'),
    path('<int:study_pk>/members/<int:pk>/delete/', StudyMemberRemoveView.as_view(),
         name="delete-member"),
    path('<int:pk>/recruitmentsettings/', StudyRecruitmentSettingsView.as_view(),
         name='recruitmentsettings'),
    path('<int:pk>/exclusioncriteria/', StudyExclusionCriteriaView.as_view(),
         name='exclusioncriteria'),
]
