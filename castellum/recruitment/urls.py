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

from .views import AppointmentFeed
from .views import ContactUpdateView
from .views import ContactView
from .views import RecruitmentViewInvited
from .views import RecruitmentViewOpen
from .views import RecruitmentViewUnsuitable
from .views import StudyChoiceView

app_name = 'recruitment'
urlpatterns = [
    path('', StudyChoiceView.as_view(), name='index'),

    path('<study_pk>/', RecruitmentViewOpen.as_view(), name='recruitment_open'),
    path('<study_pk>/invited/', RecruitmentViewInvited.as_view(),
         name='recruitment_invited'),
    path('<study_pk>/unsuitable/', RecruitmentViewUnsuitable.as_view(),
         name='recruitment_unsuitable'),
    path('<study_pk>/appointments/', AppointmentFeed(), name='appointments'),
    path('<study_pk>/<int:pk>/', ContactView.as_view(), name='contact'),
    path('<study_pk>/<int:pk>/update-contact/', ContactUpdateView.as_view(),
         name='contact-update'),
]
