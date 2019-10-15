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

from .feeds import AppointmentFeedForStudyGroup
from .feeds import AppointmentFeedForUser
from .views import AttributeSetUpdateView
from .views import ChangeGroupView
from .views import ContactUpdateView
from .views import ContactView
from .views import GroupListView
from .views import MailRecruitmentView
from .views import RecruitmentViewInvited
from .views import RecruitmentViewOpen
from .views import RecruitmentViewUnsuitable
from .views import SearchView
from .views import SubjectUpdateView

app_name = 'recruitment'
urlpatterns = [
    path('', GroupListView.as_view(), name='index'),
    path('search/', SearchView.as_view(), name='search'),
    path('appointments/<user_id>/', AppointmentFeedForUser(),
         name='all-studies-appointments'),
    path('<group_pk>/', RecruitmentViewOpen.as_view(), name='recruitment-open'),
    path('<group_pk>/invited/', RecruitmentViewInvited.as_view(),
         name='recruitment-invited'),
    path('<group_pk>/unsuitable/', RecruitmentViewUnsuitable.as_view(),
         name='recruitment-unsuitable'),
    path('<group_pk>/mail/', MailRecruitmentView.as_view(), name='mail'),
    path('<group_pk>/appointments/', AppointmentFeedForStudyGroup(), name='appointments'),
    path('<group_pk>/<int:pk>/', ContactView.as_view(), name='contact'),
    path('<group_pk>/<int:pk>/update-contact/', ContactUpdateView.as_view(),
         name='contact-update'),
    path('<group_pk>/<int:pk>/update-attributeset/', AttributeSetUpdateView.as_view(),
         name='attributeset-update'),
    path('<group_pk>/<int:pk>/update-subject/', SubjectUpdateView.as_view(),
         name='subject-update'),
    path('<group_pk>/<int:pk>/change-group/', ChangeGroupView.as_view(),
         name='change-group'),
]
