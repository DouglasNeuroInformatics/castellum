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

import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.forms import ValidationError
from django.utils import formats
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.studies.models import Study
from castellum.subjects.models import Subject
from castellum.utils.fields import DateField
from castellum.utils.fields import DateTimeField


class BaseMailBatch(models.Model):
    study = models.ForeignKey(Study, verbose_name=_('Study'), on_delete=models.CASCADE)
    datetime = models.DateTimeField(_('Sent date'), auto_now_add=True)
    contacted_size = models.PositiveIntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return formats.date_format(self.datetime, 'DATETIME_FORMAT')


class MailBatch(BaseMailBatch):
    reminded = models.BooleanField(_('Reminder already sent'), default=False)


class NewsMailBatch(BaseMailBatch):
    other_size = models.PositiveIntegerField()
    mail_subject = models.CharField(_('E-mail subject'), max_length=128)
    mail_body = models.TextField(_('E-mail body'))


class ParticipationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
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
            last_contacted_elsewhere=models.Max(
                'subject__participation__updated_at',
                filter=(
                    ~models.Q(subject__participation__study=models.F('study'))
                    & ~models.Q(
                        subject__participation__status=Participation.NOT_CONTACTED
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

    NOT_INTERESTED = 1
    VIA_POSTAL = 2
    VIA_EMAIL = 3
    NEWS_INTEREST_OPTIONS = [
        (NOT_INTERESTED, _('not interested')),
        (VIA_POSTAL, _('via postal mail')),
        (VIA_EMAIL, _('via email')),
    ]

    created_at = DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = DateTimeField(_('Updated at'), auto_now=True)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, editable=False)
    study = models.ForeignKey(Study, verbose_name=_('Study'), on_delete=models.CASCADE)
    batch = models.ForeignKey(
        MailBatch, verbose_name=_('Mail batch'), blank=True, null=True, on_delete=models.SET_NULL
    )

    status = models.IntegerField(
        _('Status of participation'), choices=STATUS_OPTIONS, default=NOT_CONTACTED
    )
    exclusion_criteria_checked = models.BooleanField(_('Subject may be suitable'), default=False)

    attempts = models.IntegerField(_('Attempts'), default=0)

    followup_date = DateField(_('Follow-up date'), blank=True, null=True)
    followup_time = models.TimeField(_('Follow-up time'), blank=True, null=True)

    news_interest = models.IntegerField(
        _('Interest in study news'), choices=NEWS_INTEREST_OPTIONS, default=NOT_INTERESTED
    )

    objects = ParticipationManager()

    class Meta:
        verbose_name = _('Study participation')
        verbose_name_plural = _('Study participations')
        unique_together = ['study', 'subject']
        permissions = [
            ('conduct_study', _('Can conduct studies')),
            ('search_participations', _('Can search for any participation')),
            ('recruit', _('Can recruit')),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_status = self.status

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

    def save(self, *args, **kwargs):
        if self.status in [self.NOT_REACHED, self.AWAITING_RESPONSE]:
            if self.status == self._old_status:
                self.attempts += 1
            else:
                self.attempts = 1
        else:
            self.attempts = 0
        super().save(*args, **kwargs)
