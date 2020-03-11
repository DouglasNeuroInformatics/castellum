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

from django.urls import path

from .views import ParticipationRequestDetailView
from .views import ResolveView
from .views import SearchView
from .views import StudyDetailView
from .views import StudyListView

app_name = 'execution'
urlpatterns = [
    path('', StudyListView.as_view(), name='index'),
    path('search/', SearchView.as_view(), name='search'),
    path('<int:study_pk>/', StudyDetailView.as_view(), name='study-detail'),
    path('<int:study_pk>/resolve/', ResolveView.as_view(), name='resolve'),
    path(
        '<int:study_pk>/<int:pk>/',
        ParticipationRequestDetailView.as_view(),
        name='participationrequest-detail',
    ),
]
