# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
        invited = self.instance.status not in Participation.INVITED_SET

        for session in self.sessions:
            key = f'appointment-{session.pk}'
            appointment = self.instance.appointment_set.filter(session=session).first()

            self.fields[key] = self.get_formfield(
                'start',
                initial=appointment.start if appointment else None,
                disabled=invited or bool(session.schedule_id),
                required=False,
            )
            self.fields[f'location-{key}'] = self.get_formfield(
                'location',
                initial=appointment.location if appointment else '',
                disabled=invited or (bool(session.schedule_id) and not appointment),
                placeholder=session.location,
            )
            self.fields[f'conductors-{key}'] = self.get_formfield(
                'assigned_conductors',
                initial=appointment.assigned_conductors.all() if appointment else [],
                queryset=self.instance.study.studymembership_set.filter(
                    user_id__in=[u.pk for u in self.instance.study.conductors]
                ),
                disabled=invited or (bool(session.schedule_id) and not appointment),
            )

    def get_formfield(self, field_name, placeholder=None, **kwargs):
        field = Appointment._meta.get_field(field_name).formfield(**kwargs)
        if placeholder:
            field.widget.attrs['placeholder'] = placeholder
        return field

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
            location = self.cleaned_data.get(f'location-{key}')
            conductors = self.cleaned_data.get(f'conductors-{key}')
            change = Appointment.change(
                session,
                participation,
                start,
                location=location,
                conductors=conductors,
            )
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
                'location': self[f'location-{key}'],
                'assigned_conductors': self[f'conductors-{key}'],
                'invitation_url': self.get_invitation_url(session),
            }
