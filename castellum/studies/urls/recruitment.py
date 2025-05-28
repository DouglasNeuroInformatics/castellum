# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import include
from django.urls import path

from ..views.recruitment import StudyMailSettingsView
from ..views.recruitment import StudyOtherStudiesView
from ..views.recruitment import StudyRecruitmentSettingsUpdateView
from ..views.recruitment import StudyRecruitmentTestMailView
from . import subjectfilters as subjectfilters_urls

urlpatterns = [
    path('', StudyRecruitmentSettingsUpdateView.as_view(), name='recruitmentsettings'),
    path('mail/', StudyMailSettingsView.as_view(), name='mailsettings'),
    path(
        'mail/test/',
        StudyRecruitmentTestMailView.as_view(),
        name='testmail-recruitment',
    ),
    path('other-studies/', StudyOtherStudiesView.as_view(), name='other-studies'),
    path('filters/', include(subjectfilters_urls)),
]
