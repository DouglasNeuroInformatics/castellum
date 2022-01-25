# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
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

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

import requests

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.recruitment.models import Participation
from castellum.utils import scheduler
from castellum.utils.forms import DateTimeField

from .models import Appointment

logger = logging.getLogger(__name__)


class AppointmentsForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.invitation_urls = {}
        for session in self.instance.study.studysession_set.all():
            key = 'appointment-{}'.format(session.pk)
            appointment = self.instance.appointment_set.filter(session=session).first()
            self.fields[key] = DateTimeField(
                label=self.format_session_name(session),
                help_text=session.reminder_text,
                initial=appointment.start if appointment else None,
                disabled=(
                    self.instance.status != Participation.INVITED
                    or bool(session.schedule_id)
                ),
                required=False,
            )
            self.fields['conductors-' + key] = Appointment._meta.get_field(
                'assigned_conductors'
            ).formfield(initial=appointment.assigned_conductors.all() if appointment else [])
            if settings.SCHEDULER_URL and session.schedule_id:
                if self.instance.status == Participation.INVITED:
                    pseudonym = get_pseudonym(self.instance.subject, session.domain)
                    try:
                        url = scheduler.create_invitation_url(session.schedule_id, pseudonym)
                    except requests.RequestException as e:
                        logger.error(
                            'Creating invitation for session {} failed: {}'.format(session.pk, e)
                        )
                        url = 'error'
                    self.invitation_urls[key] = url

    def format_session_name(self, session):
        duration = _('{}min').format(session.duration)
        types = ', '.join(str(t) for t in session.type.order_by('pk'))
        if types:
            return '{} ({}) - {}'.format(session.name, types, duration)
        else:
            return '{} - {}'.format(session.name, duration)

    def save(self):
        participation = super().save()
        self.appointment_changes = []

        for session in self.instance.study.studysession_set.all():
            key = 'appointment-{}'.format(session.pk)
            start = self.cleaned_data.get(key)
            self.appointment_changes += Appointment.change_start(session, participation, start)
            appointment = self.instance.appointment_set.filter(session=session).first()
            if appointment:
                assigned_conductors = self.cleaned_data.get('conductors-{}'.format(key))
                appointment.assigned_conductors.set(assigned_conductors)

        return participation

    @property
    def appointments(self):
        for key in self.fields:
            if key.startswith('appointment-'):
                yield {
                    'field': self[key],
                    'invitation_url': self.invitation_urls.get(key),
                    'assigned_conductors': self['conductors-' + key],
                }
