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

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.forms import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.studies.models import Study
from castellum.subjects.models import Subject
from castellum.utils.fields import DateField
from castellum.utils.fields import DateTimeField

from .attributesets import get_stat_context


class ParticipationManager(models.Manager):
    def get_queryset(self):
        others = ParticipationRevision.objects\
            .filter(current_id=models.OuterRef('id'))\
            .exclude(status=models.OuterRef('status'))
        other_status_at = others.order_by('-created_at').values('created_at')[:1]

        return super().get_queryset().annotate(
            updated_at=models.Max('revisions__created_at'),
            created_at=models.Min('revisions__created_at'),
            status_not_reached=models.Count(
                'id',
                filter=models.Q(status__in=[
                    Participation.NOT_REACHED,
                    Participation.AWAITING_RESPONSE,
                ]),
                distinct=True,
            ),
            followup_urgent=models.Count(
                'id', filter=models.Q(followup_date__lte=datetime.date.today())
            ),
            other_status_at=models.Subquery(other_status_at),
            tries=models.Count(
                'revisions',
                filter=(
                    models.Q(revisions__created_at__gt=models.F('other_status_at')) |
                    models.Q(other_status_at__isnull=True)
                ),
                distinct=True,
            ),
            last_contacted_elsewhere=models.Max(
                'subject__participation__revisions__created_at',
                filter=(
                    ~models.Q(subject__participation__study=models.F('study'))
                    & ~models.Q(
                        subject__participation__revisions__status=Participation.NOT_CONTACTED
                    )
                ),
            ),
        )


class Participation(models.Model):
    NOT_CONTACTED = 0
    NOT_REACHED = 1
    UNSUITABLE = 2
    INVITED = 3
    FOLLOWUP_APPOINTED = 4
    AWAITING_RESPONSE = 5
    STATUS_OPTIONS = [
        (NOT_CONTACTED, _('not contacted')),
        (NOT_REACHED, _('not reached')),
        (UNSUITABLE, _('unsuitable')),
        (INVITED, _('invited')),
        (FOLLOWUP_APPOINTED, _('follow-up scheduled')),
        (AWAITING_RESPONSE, _('awaiting response')),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, editable=False)
    study = models.ForeignKey(Study, verbose_name=_('Study'), on_delete=models.CASCADE)

    status = models.IntegerField(
        _('Status of participation'), choices=STATUS_OPTIONS, default=NOT_CONTACTED
    )
    exclusion_criteria_checked = models.BooleanField(_('Subject may be suitable'), default=False)

    followup_date = DateField(_('Follow-up date'), blank=True, null=True)
    followup_time = models.TimeField(_('Follow-up time'), blank=True, null=True)

    objects = ParticipationManager()

    class Meta:
        verbose_name = _('Participation')
        verbose_name_plural = _('Participations')
        unique_together = ['study', 'subject']
        permissions = [
            ('conduct_study', _('Can conduct studies')),
            ('search_participations', _('Can search for any participation')),
            ('recruit', _('Can recruit')),
        ]

    @property
    def status_open(self):
        return self.status in [
            Participation.NOT_CONTACTED,
            Participation.NOT_REACHED,
            Participation.FOLLOWUP_APPOINTED,
            Participation.AWAITING_RESPONSE,
        ]

    @cached_property
    def pseudonym(self):
        """Note that the pseudonym is generated on demand."""
        return get_pseudonym(self.subject, self.study.domain)

    @cached_property
    def appointment_today(self):
        return self.appointment_set.filter(start__date=datetime.date.today()).exists()

    @cached_property
    def match(self):
        from .. import filter_queries
        if Subject.objects.filter(
            filter_queries.study(self.study, include_unknown=False),
            pk=self.subject.pk,
        ).exists():
            return 'complete'
        elif Subject.objects.filter(
            filter_queries.study(self.study, include_unknown=True),
            pk=self.subject.pk,
        ).exists():
            return 'incomplete'
        else:
            return False

    @cached_property
    def stats(self):
        try:
            attributeset = self.subject.attributeset
        except ObjectDoesNotExist:
            return []

        stats = []
        for description, buckets in get_stat_context(self.study_id):
            value = attributeset.data.get(description.json_key)
            if len(buckets) > 1:
                bucket = description.field.get_statistics_bucket(value)
                label = dict(buckets)[bucket]
            else:
                label = description.field.get_display(value)
            stats.append((description.label, label))
        return stats

    def get_appointments(self):
        for session in self.study.studysession_set.order_by('pk'):
            try:
                appointment = self.appointment_set.get(session=session)
            except ObjectDoesNotExist:
                appointment = None
            yield session, appointment

    def clean(self):
        if self.status == self.FOLLOWUP_APPOINTED and not self.followup_date:
            raise ValidationError(_('No follow-up set'), code='invalid')
        if self.status != self.FOLLOWUP_APPOINTED and (self.followup_date or self.followup_time):
            raise ValidationError(_('Follow-up cannot be set with this status'), code='invalid')
        if (
            self.status == self.INVITED
            and self.study.has_exclusion_criteria
            and not self.exclusion_criteria_checked
        ):
            msg = _('Inclusion/exclusion criteria have not been checked')
            raise ValidationError(msg, code='invalid')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        ParticipationRevision.objects.create(
            current=self,
            status=self.status,
            exclusion_criteria_checked=self.exclusion_criteria_checked,
            followup_date=self.followup_date,
            followup_time=self.followup_time,
        )


class ParticipationRevision(models.Model):
    """Revision history for Participation.

    Each time a Participation is saved, an instance of ParticipationRevision
    is created. This way, we have a history of the Participation.

    The history is saved in separate model because of these reasons:

    -   ``Participation.pseudonym`` is unique.
    -   Saving the history in the same Participation model would degrade
        performance because the table would be filled up with old revision.
    """

    current = models.ForeignKey(
        Participation, related_name='revisions', on_delete=models.CASCADE
    )
    status = models.IntegerField(
        choices=Participation.STATUS_OPTIONS, default=Participation.NOT_CONTACTED
    )
    exclusion_criteria_checked = models.BooleanField()
    followup_date = DateField(blank=True, null=True)
    followup_time = models.TimeField(blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.created_at, self.get_status_display())


class MailBatch(models.Model):
    study = models.ForeignKey(Study, verbose_name=_('Study'), on_delete=models.CASCADE)
    datetime = models.DateTimeField(_('Sent date'), auto_now_add=True)
    contacted_size = models.PositiveIntegerField()
