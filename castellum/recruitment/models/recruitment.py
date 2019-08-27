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
from django.forms import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from castellum.studies.models import Study
from castellum.subjects.models import Subject
from castellum.utils.fields import DateTimeField

from .attributesets import AttributeSet


class ParticipationRequestManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            updated_at=models.Max('revisions__created_at'),
            created_at=models.Min('revisions__created_at'),
            status_not_reached=models.Count(
                'id', filter=models.Q(status=ParticipationRequest.NOT_REACHED)),
            appointment_today=models.Count(
                'id', filter=models.Q(appointment__date=datetime.date.today())),
            tries=models.Count(
                'revisions',
                filter=models.Q(revisions__status=ParticipationRequest.NOT_REACHED),
                distinct=True,
            ),
            last_contacted_elsewhere=models.Max(
                'subject__participationrequest__revisions__created_at',
                filter=(
                    ~models.Q(subject__participationrequest__study=models.F('study'))
                    & ~models.Q(
                        subject__participationrequest__revisions__status=ParticipationRequest.NOT_CONTACTED # noqa
                    )
                ),
            ),
        )


class ParticipationRequest(models.Model):
    NOT_CONTACTED = 0
    NOT_REACHED = 1
    UNSUITABLE = 2
    INVITED = 3
    RECALL_APPOINTED = 4
    STATUS_OPTIONS = (
        (NOT_CONTACTED, _('not contacted')),
        (NOT_REACHED, _('not reached')),
        (UNSUITABLE, _('unsuitable')),
        (INVITED, _('invited')),
        (RECALL_APPOINTED, _('recall appointed')),
    )

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, editable=False)
    study = models.ForeignKey(Study, verbose_name=_('Study'), on_delete=models.CASCADE)

    status = models.IntegerField(
        _('Status of participation request'), choices=STATUS_OPTIONS, default=NOT_CONTACTED)
    exclusion_criteria_checked = models.BooleanField(_('Subject may be suitable'), default=False)

    appointment = DateTimeField(_('Appointment'), blank=True, null=True)

    objects = ParticipationRequestManager()

    class Meta:
        verbose_name = _('Participation request')
        verbose_name_plural = _('Participation requests')
        permissions = (
            ('view_participation_pseudonyms', _('Can view participation pseudonyms')),
        )

    @property
    def status_open(self):
        return self.status in [
            ParticipationRequest.NOT_CONTACTED,
            ParticipationRequest.NOT_REACHED,
            ParticipationRequest.RECALL_APPOINTED,
        ]

    @cached_property
    def match(self):
        if AttributeSet\
                .apply_study_filter(self.study, include_unknown=False)\
                .filter(subject=self.subject)\
                .exists():
            return 'complete'
        elif AttributeSet\
                .apply_study_filter(self.study, include_unknown=True)\
                .filter(subject=self.subject)\
                .exists():
            return 'incomplete'
        else:
            return False

    def get_revisions_display(self):
        return ', '.join(str(r) for r in self.revisions.all())

    def clean(self):
        if self.status == self.RECALL_APPOINTED and not self.appointment:
            raise ValidationError(_('No appointment set'), code='invalid')
        if self.status != self.RECALL_APPOINTED and self.appointment:
            raise ValidationError(_('Appointment cannot be set with this status'), code='invalid')
        if (
            self.status == self.INVITED
            and self.study.has_exclusion_criteria
            and not self.exclusion_criteria_checked
        ):
            raise ValidationError(_('Exclusion criteria have not been checked'), code='invalid')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        ParticipationRequestRevision.objects.create(
            current=self,
            status=self.status,
            exclusion_criteria_checked=self.exclusion_criteria_checked,
            appointment=self.appointment,
        )


class ParticipationRequestRevision(models.Model):
    """Revision history for ParticipationRequest.

    Each time a ParticipationRequest is saved, an instance of ParticipationRequestRevision
    if created. This way, we have a history of the ParticipationRequest.

    The history is saved in separate model because of these reasons:

    -   ``ParticipationRequest.pseudonym`` is unique.
    -   Saving the history in the same ParticipationRequest model would degrade
        performance because the table would be filled up with old revision.
    """

    current = models.ForeignKey(
        ParticipationRequest, related_name='revisions', on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=ParticipationRequest.STATUS_OPTIONS, default=ParticipationRequest.NOT_CONTACTED)
    exclusion_criteria_checked = models.BooleanField()
    appointment = DateTimeField(blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.created_at, self.get_status_display())
