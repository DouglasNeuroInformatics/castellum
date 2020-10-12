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

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Poll


class MultiDatetimeField(forms.Field):
    widget = forms.MultipleHiddenInput

    def clean(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(_('Enter a list of values'), code='invalid_list')

        new_value = []
        for val in set(value):
            try:
                dt = datetime.datetime.strptime(val, '%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                raise ValidationError(_('Invalid datetime format'), code='invalid_datetime')
            new_value.append((dt.date(), dt.time()))
        return new_value


class PollForm(forms.ModelForm):
    timeslots = MultiDatetimeField()

    class Meta:
        model = Poll
        fields = ['title']

    def save_timeslots(self, poll):
        tuples = self.cleaned_data['timeslots']
        old = list(poll.timeslot_set.all())
        old_tuples = [(t.date, t.time) for t in old]

        for timeslot in old:
            if (timeslot.date, timeslot.time) not in tuples:
                timeslot.delete()

        for date, time in tuples:
            if (date, time) not in old_tuples:
                poll.timeslot_set.create(date=date, time=time)

    def save(self):
        poll = super().save()
        self.save_timeslots(poll)
        return poll
