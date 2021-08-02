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

import logging

from .middlewares import set_last_active

monitoring_logger = logging.getLogger('monitoring.auth')


def set_last_active_on_login(sender, user, request, **kwargs):
    set_last_active(request)


def log_login(sender, user, request, **kwargs):
    monitoring_logger.info('Login by {}'.format(user.id_for_monitoring))


def log_failed_login(sender, credentials, request, **kwargs):
    monitoring_logger.info('Failed login with username "{}"'.format(credentials['username']))


def log_logout(sender, user, request, **kwargs):
    if user:
        monitoring_logger.info('Logout by {}'.format(user.id_for_monitoring))
