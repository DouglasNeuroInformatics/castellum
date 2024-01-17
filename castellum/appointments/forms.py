# (c) 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>,
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

import logging

import requests
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.recruitment.models import Participation
from castellum.utils import scheduler

from .models import Appointment

logger = logging.getLogger(__name__)


class AppointmentsForm(forms.ModelForm):
    send_notifications = forms.BooleanField(
        label=_('Notify conductors of changes'), required=False
    )

    class Meta:
        model = Participation
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sessions = self.instance.study.studysession_set.order_by('pk')

        for session in self.sessions:
            key = f'appointment-{session.pk}'
            appointment = self.instance.appointment_set.filter(session=session).first()

            self.fields[key] = Appointment._meta.get_field('start').formfield(
                initial=appointment.start if appointment else None,
                disabled=(
                    self.instance.status not in Participation.INVITED_SET
                    or bool(session.schedule_id)
                ),
                required=False,
            )
            self.fields[f'conductors-{key}'] = (
                Appointment._meta.get_field('assigned_conductors').formfield(
                    initial=(
                        appointment.assigned_conductors.all() if appointment else []
                    ),
                    queryset=self.instance.study.studymembership_set.filter(
                        user_id__in=[u.pk for u in self.instance.study.conductors]
                    ),
                    disabled=(
                        self.instance.status not in Participation.INVITED_SET
                        or (bool(session.schedule_id) and not appointment)
                    ),
                )
            )

    def get_invitation_url(self, session):
        if (
            settings.SCHEDULER_URL
            and session.schedule_id
            and self.instance.status in Participation.INVITED_SET
        ):
            pseudonym = get_pseudonym(self.instance.subject, session.domain)
            try:
                return scheduler.create_invitation_url(session.schedule_id, pseudonym)
            except requests.RequestException as e:
                logger.error(
                    f'Creating invitation for session {session.pk} failed: {e}'
                )
                return 'error'

    def format_session_name(self, session):
        duration = _('{}min').format(session.duration)
        types = ', '.join(str(t) for t in session.type.order_by('pk'))
        if types:
            return f'{session.name} ({types}) - {duration}'
        else:
            return f'{session.name} - {duration}'

    def save(self, *args, **kwargs):
        participation = super().save(*args, **kwargs)
        self.appointment_changes = []

        for session in self.sessions:
            key = f'appointment-{session.pk}'
            start = self.cleaned_data.get(key)
            conductors = self.cleaned_data.get(f'conductors-{key}')
            change = Appointment.change(session, participation, start, conductors)
            if change:
                self.appointment_changes.append(change)

        return participation

    @property
    def appointments(self):
        for session in self.sessions:
            key = f'appointment-{session.pk}'
            yield {
                'legend': self.format_session_name(session),
                'first_reminder_days': session.first_reminder_days,
                'reminder_text': session.reminder_text,
                'field': self[key],
                'assigned_conductors': self[f'conductors-{key}'],
                'invitation_url': self.get_invitation_url(session),
            }
