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
from .views import RecruitmentView
from .views import StudyChoiceView
from .views import SubjectFilterGroupCreateView
from .views import SubjectFilterGroupDeleteView
from .views import SubjectFilterGroupView
from .views import SubjectFilterView

app_name = 'recruitment'
urlpatterns = [
    path('attributes/<slug>/', AttributeSetDetailView.as_view(), name='detail_attributes'),
    path('attributes/<slug>/update/', AttributeSetUpdateView.as_view(), name='update_attributes'),

    path('', StudyChoiceView.as_view(), name='select_study'),

    path(
        'subject_filter/<int:study_pk>/',
        SubjectFilterGroupView.as_view(),
        name='subject_filter_group'),
    path(
        'subject_filter/<int:study_pk>/create/',
        SubjectFilterGroupCreateView.as_view(),
        name='subject_filter_group_create'),
    path(
        'subject_filter/<int:study_pk>/<int:pk>/',
        SubjectFilterView.as_view(),
        name='subject_filter'),
    path(
        'subject_filter/<int:study_pk>/<int:pk>/delete/',
        SubjectFilterGroupDeleteView.as_view(),
        name='subject_filter_group_delete'),

    path('<study_pk>/', RecruitmentView.as_view(), name='select_contact'),
    path('<study_pk>/<attributeset_slug>/', ContactView.as_view(), name='contact'),
]
