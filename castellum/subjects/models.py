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

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from dateutil.relativedelta import relativedelta

from castellum.utils.fields import DateTimeField
from castellum.utils.fields import RestrictedFileField
from castellum.utils.models import TimeStampedModel


class TimeSlot(models.Model):
    hour = models.PositiveSmallIntegerField(_('hour'))

    class Meta:
        ordering = ['hour']

    def __str__(self):
        return str(self.hour)


class Subject(TimeStampedModel):
    privacy_level = models.PositiveIntegerField(
        _('Privacy level'),
        default=0,
        choices=[
            (0, _('0 (regular)')),
            (1, _('1 (increased)')),
            (2, _('2 (high)')),
        ],
    )

    to_be_deleted = models.DateField(_('To be deleted'), blank=True, null=True, help_text=_(
        'All data about this subject should be deleted or fully anonymized. '
        'This includes all data in Castellum and all data collected in studies. '
        'This option should be used when a subject requests GDPR deletion.'
    ))
    to_be_deleted_notified = models.BooleanField(default=False)

    export_requested = models.DateField(_('Export requested'), blank=True, null=True, help_text=_(
        'The subject wants to receive an export of all data we have stored about them. '
        'This includes all data in Castellum and all data collected in studies. '
        'This option should be used when a subject requests GDPR export.'
    ))

    source = models.CharField(_('Data source'), max_length=128, blank=True)

    note_hard_of_hearing = models.BooleanField(_('Hard of hearing'), default=False)
    note_difficult_to_understand = models.BooleanField(_('Difficult to understand'), default=False)
    note_abusive_language = models.BooleanField(_('Abusive language'), default=False)

    availability_monday = models.ManyToManyField(
        TimeSlot, verbose_name=_('Monday'), blank=True, related_name='+'
    )
    availability_tuesday = models.ManyToManyField(
        TimeSlot, verbose_name=_('Tuesday'), blank=True, related_name='+'
    )
    availability_wednesday = models.ManyToManyField(
        TimeSlot, verbose_name=_('Wednesday'), blank=True, related_name='+'
    )
    availability_thursday = models.ManyToManyField(
        TimeSlot, verbose_name=_('Thursday'), blank=True, related_name='+'
    )
    availability_friday = models.ManyToManyField(
        TimeSlot, verbose_name=_('Friday'), blank=True, related_name='+'
    )

    not_available_until = DateTimeField(_("not available until"), blank=True, null=True)

    class Meta:
        verbose_name = _('Subject')

    def delete(self):
        self.contact.delete()
        return super().delete()

    def get_field_names(self):
        return [
            'privacy_level',
            'availability_monday',
            'availability_tuesday',
            'availability_wednesday',
            'availability_thursday',
            'availability_friday',
            'not_available_until',
            'note_hard_of_hearing',
            'note_difficult_to_understand',
            'note_abusive_language',
            'source',
            'to_be_deleted',
            'export_requested',
        ]

    @cached_property
    def contact(self):
        from castellum.contacts.models import Contact
        contact = Contact.objects.get(subject_id=self.pk)
        contact.__dict__['subject'] = self
        return contact

    @cached_property
    def has_consent(self):
        return Consent.objects.filter(
            subject=self,
            status=Consent.CONFIRMED,
            document__is_valid=True,
        ).exists()

    @cached_property
    def has_consent_or_waiting(self):
        from castellum.recruitment import filter_queries
        return Subject.objects.filter(
            filter_queries.has_consent(include_waiting=True), pk=self.pk,
        ).exists()

    @property
    def has_consent_from_before_full_age(self):
        if not self.has_consent or not self.contact.date_of_birth:
            return False
        today = datetime.date.today()
        full_age = self.contact.date_of_birth + relativedelta(years=settings.CASTELLUM_FULL_AGE)
        return full_age < today and full_age > self.consent.updated_at.date()

    @cached_property
    def has_study_consent(self):
        from castellum.recruitment.models import Participation
        return self.participation_set.filter(status=Participation.INVITED).exists()

    @property
    def has_legal_basis(self):
        return self.has_consent_or_waiting or self.has_study_consent or self.contact.is_guardian

    @property
    def is_available(self):
        now = timezone.localtime()
        if self.not_available_until and self.not_available_until > now:
            return False
        days = [
            self.availability_monday,
            self.availability_tuesday,
            self.availability_wednesday,
            self.availability_thursday,
            self.availability_friday,
        ]
        if now.weekday() >= len(days):
            return False
        hours = days[now.weekday()]
        return hours.filter(hour=now.hour).exists()

    def get_next_available_datetime(self, start):
        days = [
            self.availability_monday,
            self.availability_tuesday,
            self.availability_wednesday,
            self.availability_thursday,
            self.availability_friday,
            None,
            None,
        ]

        # +1 accounts for the hours before start.hour on the
        # first weekday we are checking
        sliced_days = days[start.weekday():] + days[:start.weekday() + 1]
        start = timezone.localtime(start)
        for i, hours in enumerate(sliced_days):
            if not hours:
                continue
            if i == 0:
                hours = hours.filter(hour__gte=start.hour)
            earliest_hour = hours.first()
            if earliest_hour:
                return start.replace(
                    hour=earliest_hour.hour, minute=0, second=0, microsecond=0
                ) + timezone.timedelta(days=i)

    @cached_property
    def next_available(self):
        now = timezone.localtime()
        if self.not_available_until and self.not_available_until > now:
            return self.get_next_available_datetime(self.not_available_until)
        else:
            return self.get_next_available_datetime(now)


class SubjectNote(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    content = models.CharField(_('Content'), max_length=128, blank=True)


class ConsentDocument(models.Model):
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    is_valid = models.BooleanField(_('Is valid'), default=True)
    is_deprecated = models.BooleanField(_('Is deprecated'), default=False)
    file = RestrictedFileField(
        _('File'),
        blank=True,
        upload_to='consent/',
        content_types=['application/pdf'],
        max_upload_size=settings.CASTELLUM_FILE_UPLOAD_MAX_SIZE,
    )

    class Meta:
        get_latest_by = 'created_at'

    def __str__(self):
        return _('Version %i') % self.pk


class Consent(models.Model):
    WAITING = 'waiting'
    CONFIRMED = 'confirmed'

    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    subject = models.OneToOneField(Subject, on_delete=models.CASCADE)
    document = models.ForeignKey(ConsentDocument, on_delete=models.CASCADE)
    status = models.CharField(_('Status'), max_length=64, choices=[
        (WAITING, _('Waiting for confirmation')),
        (CONFIRMED, _('Confirmed')),
    ])

    class Meta:
        get_latest_by = 'document__created_at'
        verbose_name = _('Consent')


class ExportAnswer(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created_at = models.DateField(_('Created at'), auto_now_add=True)
    created_by = models.CharField(_('Created by'), max_length=150)

    class Meta:
        verbose_name = _('Export answer')
