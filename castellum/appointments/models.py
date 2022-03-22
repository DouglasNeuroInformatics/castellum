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

import datetime

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
                _('Session and participation do not belong to the same study'), code='study'
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
            old = appointment.start
            if not start:
                appointment.delete()
                return (old, None)
            else:
                if conductors is not None:
                    appointment.assigned_conductors.set(conductors)
                if start != appointment.start:
                    appointment.start = start
                    appointment.reminded = False
                    appointment.save()
                    return (old, start)
        elif start:
            appointment = participation.appointment_set.create(
                session=session,
                start=start,
            )
            if conductors is not None:
                appointment.assigned_conductors.set(conductors)
            return (None, start)
