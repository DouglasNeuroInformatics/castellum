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

import itertools

from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.recruitment.models import Participation
from castellum.utils import scheduler
from castellum.utils.expressions import MultiDurationExpr
from castellum.utils.forms import DateTimeField

from .models import MINUTE
from .models import Appointment


class AppointmentsForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.invitation_urls = {}
        for session, appointment in self.instance.get_appointments():
            key = 'appointment-{}'.format(session.pk)
            self.fields[key] = DateTimeField(
                label=self.format_session_name(session),
                help_text=session.reminder_text,
                initial=appointment.start if appointment else None,
                disabled=bool(session.schedule_id),
                required=False,
            )
            if settings.SCHEDULER_URL and session.schedule_id:
                if self.instance.status == Participation.INVITED:
                    pseudonym = get_pseudonym(self.instance.subject, session.domain)
                    url = scheduler.create_invitation_url(session.schedule_id, pseudonym)
                    self.invitation_urls[key] = url
                else:
                    self.invitation_urls[key] = 'not-invited'

    def format_session_name(self, session):
        duration = _('{}min').format(session.duration)
        types = ', '.join(str(t) for t in session.type.order_by('pk'))
        if types:
            return '{} ({}) - {}'.format(session.name, types, duration)
        else:
            return '{} - {}'.format(session.name, duration)

    def clean(self):
        cleaned_data = super().clean()

        appointments = []
        for session in self.instance.study.studysession_set.all():
            key = 'appointment-{}'.format(session.pk)
            start = cleaned_data.get(key)
            if start:
                appointments.append((session, key, start, start + session.duration * MINUTE))

        for a, b in itertools.combinations(appointments, 2):
            __, key1, start1, end1 = a
            __, key2, start2, end2 = b
            if start1 < end2 and start2 < end1:
                self.add_error(key1, _('Appointments must not overlap.'))
                self.add_error(key2, _('Appointments must not overlap.'))
                break

        qs = Appointment.objects\
            .exclude(participation=self.instance)\
            .filter(participation__status=Participation.INVITED)\
            .alias(
                # corresponds to the Appointment.end property
                end=MultiDurationExpr(models.F('start'), MINUTE, models.F('session__duration')),
            )

        for session, key, start, end in appointments:
            if session.resource and qs.filter(
                session__resource=session.resource, end__gt=start, start__lt=end,
            ).exists():
                self.add_error(key, _('The required resource is not available at this time'))

        return cleaned_data

    def save(self):
        pariticipation = super().save()
        self.appointment_changes = []

        for session, appointment in pariticipation.get_appointments():
            start = self.cleaned_data.get('appointment-{}'.format(session.pk))

            if appointment:
                if not start:
                    self.appointment_changes.append((appointment.start, None))
                    appointment.delete()
                elif start != appointment.start:
                    self.appointment_changes.append((appointment.start, start))
                    appointment.start = start
                    appointment.reminded = False
                    appointment.show_up = Appointment.SHOWUP  # reset to default
                    appointment.save()
            elif start:
                self.appointment_changes.append((None, start))
                pariticipation.appointment_set.create(
                    session=session,
                    start=start,
                )

        return pariticipation

    @property
    def appointments(self):
        for name in self.fields:
            if name.startswith('appointment-'):
                yield {
                    'field': self[name],
                    'invitation_url': self.invitation_urls.get(name)
                }
