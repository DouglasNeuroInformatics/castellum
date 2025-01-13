# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
from collections import namedtuple

from django.db import models
from django.forms import ValidationError
from django.utils import formats
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from castellum.recruitment.models import Participation
from castellum.studies.models import StudyMembership
from castellum.studies.models import StudySession
from castellum.utils.expressions import MultiDurationExpr
from castellum.utils.fields import DateTimeField

MINUTE = datetime.timedelta(seconds=60)

AppointmentState = namedtuple('AppointmentState', ['start', 'assigned_conductors'])


class AppointmentQuerySet(models.QuerySet):
    def annotate_end(self):
        return self.alias(
            # corresponds to the Appointment.end property
            end=MultiDurationExpr(
                models.F('start'), MINUTE, models.F('session__duration')
            ),
        )


class Appointment(models.Model):
    session = models.ForeignKey(
        StudySession, verbose_name=_('Session'), on_delete=models.CASCADE
    )
    start = DateTimeField(_('Start'))
    first_reminder_sent = models.BooleanField(_('First reminder sent'), default=False)
    second_reminder_sent = models.BooleanField(_('Second reminder sent'), default=False)
    participation = models.ForeignKey(
        Participation,
        on_delete=models.CASCADE,
        verbose_name=_('Participation'),
    )
    assigned_conductors = models.ManyToManyField(
        StudyMembership,
        verbose_name=_('Assigned conductors'),
        blank=True,
        related_name='+',
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
                _('Session and participation do not belong to the same study'),
                code='study',
            )

    def save(self, *args, **kwargs):
        # updates Subject.updated_at
        self.participation.subject.save()
        super().save(*args, **kwargs)

    @property
    def end(self):
        return self.start + MINUTE * self.session.duration

    @staticmethod
    def change(session, participation, start, conductors=None):
        appointment = participation.appointment_set.filter(session=session).first()

        if appointment:
            old = AppointmentState(
                appointment.start,
                {c.user for c in appointment.assigned_conductors.all()},
            )
            if not start:
                appointment.delete()
                return (old, None)
            else:
                if conductors is not None:
                    appointment.assigned_conductors.set(conductors)
                if start != appointment.start:
                    appointment.start = start
                    appointment.first_reminder_sent = False
                    appointment.second_reminder_sent = False
                    appointment.save()
        elif start:
            old = None
            appointment = participation.appointment_set.create(
                session=session,
                start=start,
            )
            if conductors is not None:
                appointment.assigned_conductors.set(conductors)
        else:
            return None

        new = AppointmentState(
            start,
            {c.user for c in appointment.assigned_conductors.all()},
        )
        if old != new:
            return (old, new)
