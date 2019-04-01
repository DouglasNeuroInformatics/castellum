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

from .views.attributesets import AttributeSetUpdateView
from .views.contacts import ContactStudiesView
from .views.contacts import ContactUpdateView
from .views.recruitment import ContactView
from .views.recruitment import RecruitmentViewInvited
from .views.recruitment import RecruitmentViewOpen
from .views.recruitment import RecruitmentViewUnsuitable
from .views.recruitment import StudyChoiceView
from .views.subjectfilters import FilterGroupCreateView
from .views.subjectfilters import FilterGroupDeleteView
from .views.subjectfilters import FilterGroupDuplicateView
from .views.subjectfilters import FilterGroupListView
from .views.subjectfilters import FilterGroupUpdateView

app_name = 'recruitment'
urlpatterns = [
    path('attributes/<slug>/update/', AttributeSetUpdateView.as_view(), name='attributes_update'),

    path('contacts/<slug>/studies/', ContactStudiesView.as_view(), name='contacts_studies'),

    path('', StudyChoiceView.as_view(), name='index'),

    path(
        'filter/<int:study_pk>/',
        FilterGroupListView.as_view(),
        name='filtergroup_index'),
    path(
        'filter/<int:study_pk>/create/',
        FilterGroupCreateView.as_view(),
        name='filtergroup_create'),
    path(
        'filter/<int:study_pk>/<int:pk>/delete/',
        FilterGroupDeleteView.as_view(),
        name='filtergroup_delete'),
    path(
        'filter/<int:study_pk>/<int:pk>/',
        FilterGroupUpdateView.as_view(),
        name='filtergroup_update'),
    path(
        'filter/<int:study_pk>/<int:pk>/duplicate/',
        FilterGroupDuplicateView.as_view(),
        name='filtergroup_duplicate'),

    path('<study_pk>/', RecruitmentViewOpen.as_view(), name='recruitment_open'),
    path('<study_pk>/invited/', RecruitmentViewInvited.as_view(),
         name='recruitment_invited'),
    path('<study_pk>/unsuitable/', RecruitmentViewUnsuitable.as_view(),
         name='recruitment_unsuitable'),
    path('<study_pk>/<slug>/', ContactView.as_view(), name='contact'),
    path('<study_pk>/<slug>/update-contact/', ContactUpdateView.as_view(),
         name='contact-update'),
]
