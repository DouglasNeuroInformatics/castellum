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

from django.conf import settings
from django.db import models
from django.forms import ValidationError
from django.utils import formats
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from castellum.studies.models import Study
from castellum.studies.models import StudyMembership
from castellum.subjects.models import Subject
from castellum.utils.fields import DateField
from castellum.utils.fields import DateTimeField
from castellum.utils.fields import RestrictedFileField


def consent_upload_to(instance, filename):
    assert instance.pk
    return 'studyconsents/{}/{}/{}'.format(
        instance.study.pk, instance.pk, filename
    )


class BaseMailBatch(models.Model):
    study = models.ForeignKey(Study, verbose_name=_('Study'), on_delete=models.CASCADE)
    datetime = models.DateTimeField(_('Sent date'), auto_now_add=True)
    contacted_size = models.PositiveIntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return formats.date_format(timezone.localtime(self.datetime), 'DATETIME_FORMAT')


class MailBatch(BaseMailBatch):
    reminded = models.DateTimeField(_('Reminder date'), blank=True, null=True)


class NewsMailBatch(BaseMailBatch):
    other_size = models.PositiveIntegerField()
    mail_subject = models.CharField(_('E-mail subject'), max_length=128)
    mail_body = models.TextField(_('E-mail body'))


class ExecutionTag(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=64)
    color = models.CharField(_('Color'), max_length=16, default='info', choices=[
        ('info', _('Info')),
        ('success', _('Success')),
        ('danger', _('Danger')),
        ('warning', _('Warning')),
        ('primary', _('Primary')),
    ])

    def __str__(self):
        return self.name


class ParticipationQuerySet(models.QuerySet):
    def with_sort_properties(self):
        recent = timezone.now() - settings.CASTELLUM_RECENT_ACTIVITY_PERIOD

        return self.annotate(
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
                    & ~models.Q(subject__participation__status=Participation.NOT_CONTACTED)
                ),
            ),
            recent_participation_count=models.Count(
                'subject__participation',
                filter=models.Q(
                    subject__participation__updated_at__gt=recent,
                    subject__participation__status=Participation.INVITED,
                ),
                distinct=True,
            ),
        )

    def with_appointment_count(self):
        return self.annotate(appointment_count=models.Count('appointment', distinct=True))

    def with_assigned_to_me(self, user):
        return self.annotate(
            assigned_to_me=models.Count('id', filter=models.Q(assigned_recruiter__user=user)),
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
        (FOLLOWUP_APPOINTED, _('follow-up scheduled')),
        (AWAITING_RESPONSE, _('awaiting response')),
        (INVITED, _('participating')),
        (UNSUITABLE, _('excluded')),
    ]

    NOT_INTERESTED = 1
    VIA_POSTAL = 2
    VIA_EMAIL = 3
    NEWS_INTEREST_OPTIONS = [
        (NOT_INTERESTED, _('not interested')),
        (VIA_POSTAL, _('via postal mail')),
        (VIA_EMAIL, _('via email')),
    ]

    TOOLTIPS = {
        'dropped_out': _('The subject did not complete the study.'),
        'excluded_by_cleanup': _(
            'The subject has been excluded through the bulk cleanup feature.'
        ),
        'recently_active': _('The subject has recently been in contact with our institute.'),
        'recently_contacted': _('The subject was recently contacted in another recruitment.'),
        'pseudonyms_deleted': _(
            'It is no longer possible to know which dataset belongs to this subject'
        ),
        'status': {
            NOT_CONTACTED: _('The subject has not yet been contacted.'),
            NOT_REACHED: _('The last contact attempt has failed.'),
            UNSUITABLE: _('The subject will not participate in the study.'),
            INVITED: _('The subject has agreed to participate in the study.'),
            FOLLOWUP_APPOINTED: _('The subject has agreed on a date and time for a follow-up.'),
            AWAITING_RESPONSE: _(
                'The subject has been contacted (e.g. by email) but has not yet responded.'
            ),
        }
    }

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
    dropped_out = models.BooleanField(_('Dropped out'), default=False)
    excluded_by_cleanup = models.BooleanField(_('Excluded by cleanup'), default=False)

    attempts = models.IntegerField(_('Attempts'), default=0)

    followup_date = DateField(_('Follow-up date'), blank=True, null=True)
    followup_time = models.TimeField(_('Follow-up time'), blank=True, null=True)

    news_interest = models.IntegerField(
        _('Interest in study news'), choices=NEWS_INTEREST_OPTIONS, default=NOT_INTERESTED
    )
    execution_tags = models.ManyToManyField(
        ExecutionTag, verbose_name=_('Execution tags'), blank=True
    )
    assigned_recruiter = models.ForeignKey(
        StudyMembership,
        verbose_name=_('Assigned recruiter'),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='+',
    )

    consent = RestrictedFileField(
        _('Study consent'),
        blank=True,
        upload_to=consent_upload_to,
        content_types=['application/pdf'],
        max_upload_size=settings.CASTELLUM_FILE_UPLOAD_MAX_SIZE,
    )

    objects = ParticipationQuerySet.as_manager()

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

    def get_status_tooltip(self):
        return self.TOOLTIPS['status'][self.status]

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

        if self.status == self.INVITED:
            ReliabilityEntry.objects.get_or_create(study=self.study, subject=self.subject)

        if self.status != self.UNSUITABLE:
            self.excluded_by_cleanup = False

        if (
            self.status in [self.INVITED, self.UNSUITABLE, self.FOLLOWUP_APPOINTED]
            and self.status != self._old_status
            and not self.excluded_by_cleanup
        ):
            # updates Subject.updated_at
            self.subject.save()

        super().save(*args, **kwargs)


class ReliabilityEntry(models.Model):
    study = models.ForeignKey(Study, verbose_name=_('Study'), on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, verbose_name=_('Subject'), on_delete=models.CASCADE)
    was_reliable = models.BooleanField(_('Was reliable'), default=True)

    class Meta:
        verbose_name = _('Reliability entry')
        verbose_name_plural = _('Reliability entry')

    def save(self, *args, **kwargs):
        # updates Subject.updated_at
        self.subject.save()
        super().save(*args, **kwargs)
