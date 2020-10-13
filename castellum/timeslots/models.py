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

import datetime

from django.db import models
from django.utils import formats
from django.utils.translation import gettext_lazy as _


class Poll(models.Model):
    title = models.CharField(_('Title'), max_length=254)

    def __str__(self):
        return self.title


class Timeslot(models.Model):
    poll = models.ForeignKey(Poll, verbose_name=_('Poll'), on_delete=models.CASCADE)
    # date and time fields are always naive -- which is what we want
    # https://docs.djangoproject.com/en/3.0/topics/i18n/timezones/#naive-and-aware-datetime-objects
    date = models.DateField(_('Date'))
    time = models.TimeField(_('Time'))

    @property
    def datetime(self):
        return datetime.datetime.combine(self.date, self.time)

    class Meta:
        unique_together = ['poll', 'date', 'time']
        ordering = ['date', 'time']

    def __str__(self):
        return '%s %s' % (formats.date_format(self.date), formats.time_format(self.time))


class Invitation(models.Model):
    pseudonym = models.CharField(_('Pseudonym'), max_length=254)
    poll = models.ForeignKey(Poll, verbose_name=_('Poll'), on_delete=models.CASCADE)
    timeslot = models.OneToOneField(
        Timeslot,
        verbose_name=_('Timeslot'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        unique_together = ['poll', 'pseudonym']

    def __str__(self):
        return '%s:%s' % (self.poll, self.pseudonym)
