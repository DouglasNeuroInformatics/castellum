# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
