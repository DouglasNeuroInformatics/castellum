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


def get_settings(request):
    return {
        'CASTELLUM_ENABLE_STUDY_EXPORT': settings.CASTELLUM_ENABLE_STUDY_EXPORT,
        'CASTELLUM_STUDY_STATUS_NOTIFICATION_TO': settings.CASTELLUM_STUDY_STATUS_NOTIFICATION_TO,
        'CASTELLUM_GENERAL_EXCLUSION_CRITERIA': settings.CASTELLUM_GENERAL_EXCLUSION_CRITERIA,
        'CASTELLUM_GENERAL_RECRUITMENT_TEXT': settings.CASTELLUM_GENERAL_RECRUITMENT_TEXT,
        'SCHEDULER_URL': settings.SCHEDULER_URL,

        # Error templates do not get a context. Invert this value to
        # avoid demo warnings in that case.
        'DEMO': not settings.PRODUCTION,
    }
