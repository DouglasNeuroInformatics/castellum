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

import datetime

from django.db import models
from django.utils.formats import date_format
from django.utils.formats import time_format
from django.utils.translation import gettext_lazy as _

from castellum.studies.models import StudySession
from castellum.utils.fields import DateTimeField

from .recruitment import ParticipationRequest


class AppointmentManager(models.Manager):
    def get_queryset(self):
        minute = datetime.timedelta(seconds=60)
        return super().get_queryset().annotate(
            end=models.ExpressionWrapper(
                models.F('start') + minute * models.F('session__duration'),
                output_field=models.DateTimeField(),
            )
        )


class Appointment(models.Model):
    session = models.ForeignKey(StudySession, verbose_name=_('Session'), on_delete=models.CASCADE)
    start = DateTimeField(_('Start'))
    participant = models.ForeignKey(
        ParticipationRequest,
        on_delete=models.CASCADE,
        verbose_name=_('Participant'),
        blank=True,
        null=True,
    )

    objects = AppointmentManager()

    class Meta:
        ordering = ('start',)

    def __str__(self):
        return '%s %s' % (date_format(self.start), time_format(self.start))
