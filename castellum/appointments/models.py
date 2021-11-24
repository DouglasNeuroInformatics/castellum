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

import datetime

from django.db import models
from django.forms import ValidationError
from django.utils import formats
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from castellum.recruitment.models import Participation
from castellum.studies.models import StudySession
from castellum.utils.expressions import MultiDurationExpr
from castellum.utils.fields import DateTimeField

MINUTE = datetime.timedelta(seconds=60)


class AppointmentQuerySet(models.QuerySet):
    def annotate_end(self):
        return self.alias(
            # corresponds to the Appointment.end property
            end=MultiDurationExpr(models.F('start'), MINUTE, models.F('session__duration')),
        )


class Appointment(models.Model):
    session = models.ForeignKey(StudySession, verbose_name=_('Session'), on_delete=models.CASCADE)
    start = DateTimeField(_('Start'))
    reminded = models.BooleanField(_('Reminded'), default=False)
    participation = models.ForeignKey(
        Participation,
        on_delete=models.CASCADE,
        verbose_name=_('Participation'),
    )

    objects = AppointmentQuerySet.as_manager()

    class Meta:
        verbose_name = _('Appointment')
        ordering = ['start']
        unique_together = ['session', 'participation']
        permissions = [
            ('view_current_appointments', _('Can view current appointments')),
        ]

    def __str__(self):
        return formats.date_format(timezone.localtime(self.start), 'DATETIME_FORMAT')

    def clean(self):
        if self.session.study != self.participation.study:
            raise ValidationError(
                _('Session and participation do not belong to the same study'), code='study'
            )

    @property
    def end(self):
        return self.start + MINUTE * self.session.duration
