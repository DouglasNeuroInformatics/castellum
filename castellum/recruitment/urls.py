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
from .views import RemoveSubjectFilterView
from .views import StudyChoiceView
from .views import SubjectChoiceView
from .views import SubjectFilterView

app_name = 'recruitment'
urlpatterns = [
    path('attributes/<slug>/', AttributeSetDetailView.as_view(), name='detail_attributes'),
    path('attributes/<slug>/update/', AttributeSetUpdateView.as_view(), name='update_attributes'),

    path('', StudyChoiceView.as_view(), name='select_study'),
    path('<study_pk>/', SubjectChoiceView.as_view(), name='select_subject'),
    path('<study_pk>/<subject_slug>/', ContactView.as_view(), name='contact'),

    path('subject_filter/<int:study_id>', SubjectFilterView.as_view(), name='subject_filter'),
    path('subject_filter/<int:study_id>/remove/<int:filter_id>',
         RemoveSubjectFilterView.as_view(),
         name='remove_subject_filter'),
]
