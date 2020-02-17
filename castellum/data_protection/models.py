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

from django.db import models
from django.utils.translation import gettext_lazy as _

from castellum.data_protection import monitoring_logger


class MonitoringEntry(models.Model):
    REASONS = [
        (monitoring_logger.LOGIN, _('Login')),
        (monitoring_logger.FAILED_LOGIN, _('Failed login')),
        (monitoring_logger.LOGOUT, _('Logout')),
        (monitoring_logger.STUDY_DELETION, _('Study deletion')),
        (monitoring_logger.ATTRIBUTESET_UPDATE, _('Attributeset update')),
        (monitoring_logger.SUBJECT_DATA_UPDATE, _('Subject data update')),
        (monitoring_logger.SUBJECT_SEARCH, _('Subject search')),
        (monitoring_logger.SUBJECT_DELETION, _('Subject deletion')),
        (monitoring_logger.GDPR_EXPORT, _('GDPR export')),
        (monitoring_logger.PARTICIPATIONREQUEST_DELETION, _('Participationrequest deletion')),
    ]

    datetime = models.DateTimeField(_('Datetime'), auto_now_add=True)
    message = models.CharField(_('Message'), max_length=128)
    reason = models.SmallIntegerField(_('Reason'), choices=REASONS)

    class Meta:
        ordering = ['-datetime']
