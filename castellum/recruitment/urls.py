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

from .views import AttributeSetDetailView
from .views import AttributeSetUpdateView
from .views import ContactView
from .views import FilterCreateView
from .views import FilterDeleteView
from .views import FilterListView
from .views import FilterUpdateView
from .views import RecruitmentView
from .views import StudyChoiceView

app_name = 'recruitment'
urlpatterns = [
    path('attributes/<slug>/', AttributeSetDetailView.as_view(), name='detail_attributes'),
    path('attributes/<slug>/update/', AttributeSetUpdateView.as_view(), name='update_attributes'),

    path('', StudyChoiceView.as_view(), name='select_study'),

    path(
        'filter/<int:study_pk>/',
        FilterListView.as_view(),
        name='filter_index'),
    path(
        'filter/<int:study_pk>/create/',
        FilterCreateView.as_view(),
        name='filter_create'),
    path(
        'filter/<int:study_pk>/<int:pk>/',
        FilterUpdateView.as_view(),
        name='filter_update'),
    path(
        'filter/<int:study_pk>/<int:pk>/delete/',
        FilterDeleteView.as_view(),
        name='filter_delete'),

    path('<study_pk>/', RecruitmentView.as_view(), name='select_contact'),
    path('<study_pk>/<attributeset_slug>/', ContactView.as_view(), name='contact'),
]
