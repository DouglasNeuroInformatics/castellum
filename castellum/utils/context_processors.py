# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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

import castellum


def get_settings(request):
    return {
        'CASTELLUM_VERSION': castellum.__version__,
        'CASTELLUM_RELEASE_DATE': castellum.__release_date__,
        'CASTELLUM_SITE_TITLE': settings.CASTELLUM_SITE_TITLE,
        'CASTELLUM_SITE_LOGO': settings.CASTELLUM_SITE_LOGO,
        'CASTELLUM_LOGOUT_TIMEOUT': settings.CASTELLUM_LOGOUT_TIMEOUT,
        'CASTELLUM_ENABLE_STUDY_EXPORT': settings.CASTELLUM_ENABLE_STUDY_EXPORT,
        'CASTELLUM_GENERAL_RECRUITMENT_TEXT': settings.CASTELLUM_GENERAL_RECRUITMENT_TEXT,
        'CASTELLUM_SUBJECT_CREATION_REQUESTS_ENABLED': settings.CASTELLUM_SUBJECT_CREATION_REQUESTS_ENABLED,  # noqa
        'SCHEDULER_URL': settings.SCHEDULER_URL,

        # Error templates do not get a context. Invert this value to
        # avoid demo warnings in that case.
        'DEMO': not settings.PRODUCTION,
    }
