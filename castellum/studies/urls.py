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

from django.conf import settings
from django.urls import path

from .views.members import StudyMembershipRemoveView
from .views.members import StudyMembershipUpdateView
from .views.members import StudyMembersView
from .views.recruitment import OneTimeInvitationMailRecruitmentView
from .views.recruitment import StudyExcludedStudiesView
from .views.recruitment import StudyExclusionCriteriaView
from .views.recruitment import StudyMailSettingsView
from .views.recruitment import StudyRecruitmentSettingsUpdateView
from .views.recruitment import StudySessionCreateView
from .views.recruitment import StudySessionDeleteView
from .views.recruitment import StudySessionsView
from .views.recruitment import StudySessionUpdateView
from .views.studies import StudyCreateView
from .views.studies import StudyDeleteView
from .views.studies import StudyDetailView
from .views.studies import StudyExportView
from .views.studies import StudyFinishRecruitmentView
from .views.studies import StudyImportView
from .views.studies import StudyIndexView
from .views.studies import StudyStartRecruitmentView
from .views.studies import StudyUpdateView
from .views.subjectfilters import FilterGroupCreateView
from .views.subjectfilters import FilterGroupDeleteView
from .views.subjectfilters import FilterGroupDuplicateView
from .views.subjectfilters import FilterGroupListView
from .views.subjectfilters import FilterGroupUpdateView

app_name = 'studies'
urlpatterns = [
    path('', StudyIndexView.as_view(), name='index'),
    path('create/', StudyCreateView.as_view(), name='create'),
    path('<int:pk>/', StudyDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', StudyUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', StudyDeleteView.as_view(), name='delete'),
    path('<int:study_pk>/start/', StudyStartRecruitmentView.as_view(), name='start'),
    path(
        '<int:study_pk>/finish-recruitment/',
        StudyFinishRecruitmentView.as_view(),
        name='finish-recruitment',
    ),
    path('<int:pk>/members/', StudyMembersView.as_view(), name='members'),
    path('<int:study_pk>/members/<int:pk>/', StudyMembershipUpdateView.as_view(), name='member'),
    path(
        '<int:study_pk>/members/<int:pk>/delete/',
        StudyMembershipRemoveView.as_view(),
        name="delete-member",
    ),
    path(
        '<int:pk>/recruitmentsettings/',
        StudyRecruitmentSettingsUpdateView.as_view(),
        name='recruitmentsettings',
    ),
    path(
        '<int:pk>/recruitmentsettings/exclusioncriteria/',
        StudyExclusionCriteriaView.as_view(),
        name='exclusioncriteria',
    ),
    path(
        '<int:pk>/recruitmentsettings/mail/',
        StudyMailSettingsView.as_view(),
        name='mailsettings',
    ),
    path(
        '<int:pk>/recruitmentsettings/excluded-studies/',
        StudyExcludedStudiesView.as_view(),
        name='excluded-studies',
    ),
    path('<int:pk>/recruitmentsettings/sessions/', StudySessionsView.as_view(), name='sessions'),
    path(
        '<int:study_pk>/recruitmentsettings/sessions/new/',
        StudySessionCreateView.as_view(),
        name='session-create',
    ),
    path(
        '<int:study_pk>/recruitmentsettings/sessions/<int:pk>/',
        StudySessionUpdateView.as_view(),
        name='session-update',
    ),
    path(
        '<int:study_pk>/recruitmentsettings/sessions/<int:pk>/delete/',
        StudySessionDeleteView.as_view(),
        name='session-delete',
    ),
    path(
        '<int:study_pk>/recruitmentsettings/filters/',
        FilterGroupListView.as_view(),
        name='filtergroup-index',
    ),
    path(
        '<int:study_pk>/recruitmentsettings/filters/create/',
        FilterGroupCreateView.as_view(),
        name='filtergroup-create',
    ),
    path(
        '<int:study_pk>/recruitmentsettings/filters/<int:pk>/',
        FilterGroupUpdateView.as_view(),
        name='filtergroup-update',
    ),
    path(
        '<int:study_pk>/recruitmentsettings/filters/<int:pk>/delete/',
        FilterGroupDeleteView.as_view(),
        name='filtergroup-delete',
    ),
    path(
        '<int:study_pk>/recruitmentsettings/filters/<int:pk>/duplicate/',
        FilterGroupDuplicateView.as_view(),
        name='filtergroup-duplicate',
    ),
    path('<int:pk>/mail/', OneTimeInvitationMailRecruitmentView.as_view(), name='mail'),
]

if settings.CASTELLUM_ENABLE_STUDY_EXPORT:
    urlpatterns += [
        path('import/', StudyImportView.as_view(), name='import'),
        path('<int:pk>/export/', StudyExportView.as_view(), name='export'),
    ]
