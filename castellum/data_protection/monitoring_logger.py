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


LOGIN = 0
FAILED_LOGIN = 1
LOGOUT = 2
STUDY_DELETION = 3
ATTRIBUTESET_UPDATE = 4
SUBJECT_DATA_UPDATE = 5
SUBJECT_SEARCH = 6
SUBJECT_DELETION = 7
GDPR_EXPORT = 8
PARTICIPATIONREQUEST_DELETION = 9


def info(message, reason):
    from .models import MonitoringEntry
    MonitoringEntry.objects.create(message=message, reason=reason)
