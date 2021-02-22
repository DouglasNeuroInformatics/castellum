# (c) 2018-2021
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

from .feeds import AppointmentFeed
from .feeds import FollowUpFeedForStudy
from .feeds import FollowUpFeedForUser
from .feeds import ResourceFeed
from .views import AdditionalInfoUpdateView
from .views import AttributesUpdateView
from .views import CalendarView
from .views import ContactUpdateView
from .views import ContactView
from .views import DataProtectionUpdateView
from .views import MailRecruitmentCleanupView
from .views import MailRecruitmentView
from .views import RecruitmentCleanupView
from .views import RecruitmentViewInvited
from .views import RecruitmentViewOpen
from .views import RecruitmentViewUnsuitable
from .views import SchedulerPingView

app_name = 'recruitment'
urlpatterns = [
    path('followups/', FollowUpFeedForUser(), name='followups-user-feed'),
    path('resources/<int:pk>/', ResourceFeed(), name='resource-feed'),
    path('scheduler-ping/<int:schedule_id>/<pseudonym>/', SchedulerPingView.as_view()),
    path('<int:study_pk>/', RecruitmentViewOpen.as_view(), name='recruitment-open'),
    path('<int:study_pk>/invited/', RecruitmentViewInvited.as_view(), name='recruitment-invited'),
    path(
        '<int:study_pk>/unsuitable/',
        RecruitmentViewUnsuitable.as_view(),
        name='recruitment-unsuitable',
    ),
    path('<int:study_pk>/mail/', MailRecruitmentView.as_view(), name='mail'),
    path(
        '<int:study_pk>/mail/<int:pk>/cleanup/',
        MailRecruitmentCleanupView.as_view(),
        name='mail-cleanup',
    ),
    path('<int:study_pk>/cleanup/', RecruitmentCleanupView.as_view(), name='cleanup'),
    path('<int:pk>/calendar/', CalendarView.as_view(), name='calendar'),
    path('<int:pk>/calendar/feed/', AppointmentFeed(), name='calendar-feed'),
    path('<int:study_pk>/followups/', FollowUpFeedForStudy(), name='followups-feed'),
    path('<int:study_pk>/<int:pk>/', ContactView.as_view(), name='contact'),
    path(
        '<int:study_pk>/<int:pk>/update-contact/',
        ContactUpdateView.as_view(),
        name='contact-update',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-attributes/',
        AttributesUpdateView.as_view(),
        name='attributes-update',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-data-protection/',
        DataProtectionUpdateView.as_view(),
        name='data-protection-update',
    ),
    path(
        '<int:study_pk>/<int:pk>/update-additional-info/',
        AdditionalInfoUpdateView.as_view(),
        name='additional-info-update',
    ),
]
