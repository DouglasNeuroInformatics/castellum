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

from django.urls import path

from ..views.sessions import StudyReminderTestMailView
from ..views.sessions import StudySessionCreateView
from ..views.sessions import StudySessionDeleteView
from ..views.sessions import StudySessionsView
from ..views.sessions import StudySessionUpdateView

urlpatterns = [
    path('', StudySessionsView.as_view(), name='sessions'),
    path('new/', StudySessionCreateView.as_view(), name='session-create'),
    path('<int:pk>/', StudySessionUpdateView.as_view(), name='session-update'),
    path('<int:pk>/delete/', StudySessionDeleteView.as_view(), name='session-delete'),
    path(
        '<int:pk>/testmail/',
        StudyReminderTestMailView.as_view(),
        name='testmail-reminder',
    ),
]
