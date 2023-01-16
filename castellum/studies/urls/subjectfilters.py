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

from ..views.subjectfilters import FilterGroupCreateView
from ..views.subjectfilters import FilterGroupDeleteView
from ..views.subjectfilters import FilterGroupDuplicateView
from ..views.subjectfilters import FilterGroupListView
from ..views.subjectfilters import FilterGroupUpdateView

urlpatterns = [
    path('', FilterGroupListView.as_view(), name='filtergroup-index'),
    path('create/', FilterGroupCreateView.as_view(), name='filtergroup-create'),
    path('<int:pk>/', FilterGroupUpdateView.as_view(), name='filtergroup-update'),
    path('<int:pk>/delete/', FilterGroupDeleteView.as_view(), name='filtergroup-delete'),
    path('<int:pk>/duplicate/', FilterGroupDuplicateView.as_view(), name='filtergroup-duplicate'),
]
