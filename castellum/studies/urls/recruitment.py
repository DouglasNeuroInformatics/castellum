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

from django.urls import include
from django.urls import path

from ..views.recruitment import FilterTrialConvertView
from ..views.recruitment import StudyExcludedStudiesView
from ..views.recruitment import StudyExclusionCriteriaView
from ..views.recruitment import StudyMailSettingsView
from ..views.recruitment import StudyRecruitmentSettingsUpdateView
from ..views.recruitment import StudyRecruitmentTestMailView
from . import subjectfilters as subjectfilters_urls

urlpatterns = [
    path('', StudyRecruitmentSettingsUpdateView.as_view(), name='recruitmentsettings'),
    path('exclusioncriteria/', StudyExclusionCriteriaView.as_view(), name='exclusioncriteria'),
    path('mail/', StudyMailSettingsView.as_view(), name='mailsettings'),
    path('mail/test/', StudyRecruitmentTestMailView.as_view(), name='testmail-recruitment'),
    path('excluded-studies/', StudyExcludedStudiesView.as_view(), name='excluded-studies'),
    path('convert/', FilterTrialConvertView.as_view(), name='filtertrial-convert'),
    path('filters/', include(subjectfilters_urls)),
]
