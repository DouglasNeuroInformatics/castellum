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
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from castellum.utils.fields import DateTimeField


class TimeSlot(models.Model):
    hour = models.PositiveSmallIntegerField(_('hour'))

    class Meta:
        ordering = ['hour']

    def __str__(self):
        return str(self.hour)


class Subject(models.Model):
    privacy_level = models.PositiveIntegerField(
        _("privacy level"),
        default=0,
        choices=[
            (0, _('0 (regular)')),
            (1, _('1 (increased)')),
            (2, _('2 (high)'))
        ],
    )

    note_hard_of_hearing = models.BooleanField(_('Hard of hearing'), default=False)
    note_difficult_to_understand = models.BooleanField(_('Difficult to understand'), default=False)
    note_abusive_language = models.BooleanField(_('Abusive language'), default=False)

    availability_monday = models.ManyToManyField(
        TimeSlot, verbose_name=_("monday"), blank=True, related_name='+')
    availability_tuesday = models.ManyToManyField(
        TimeSlot, verbose_name=_("tuesday"), blank=True, related_name='+')
    availability_wednesday = models.ManyToManyField(
        TimeSlot, verbose_name=_("wednesday"), blank=True, related_name='+')
    availability_thursday = models.ManyToManyField(
        TimeSlot, verbose_name=_("thursday"), blank=True, related_name='+')
    availability_friday = models.ManyToManyField(
        TimeSlot, verbose_name=_("friday"), blank=True, related_name='+')

    not_available_until = DateTimeField(_("not available until"), blank=True, null=True)

    class Meta:
        verbose_name = _('Subject')

    def get_field_names(self):
        return [
            'privacy_level',
            'availability_monday',
            'availability_tuesday',
            'availability_wednesday',
            'availability_thursday',
            'availability_friday',
            'not_available_until',
        ]

    @property
    def is_available(self):
        now = timezone.localtime()
        if self.not_available_until and self.not_available_until > now:
            return False
        days = [
            self.availability_monday,
            self.availability_tuesday,
            self.availability_wednesday,
            self.availability_thursday,
            self.availability_friday,
        ]
        if now.weekday() >= len(days):
            return False
        hours = days[now.weekday()]
        return hours.filter(hour=now.hour).exists()

    def get_availability_monday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_monday.all())

    def get_availability_tuesday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_tuesday.all())

    def get_availability_wednesday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_wednesday.all())

    def get_availability_thursday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_thursday.all())

    def get_availability_friday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_friday.all())
