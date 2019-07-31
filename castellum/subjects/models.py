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

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from castellum.utils.fields import DateTimeField
from castellum.utils.fields import RestrictedFileField
from castellum.utils.models import TimeStampedModel


class TimeSlot(models.Model):
    hour = models.PositiveSmallIntegerField(_('hour'))

    class Meta:
        ordering = ['hour']

    def __str__(self):
        return str(self.hour)


class Availability(models.Model):


class Subject(TimeStampedModel):
    privacy_level = models.PositiveIntegerField(
        _('Privacy level'),
        default=0,
        choices=[
            (0, _('0 (regular)')),
            (1, _('1 (increased)')),
            (2, _('2 (high)'))
        ],
    )

    note_hard_of_hearing = models.BooleanField(_('Hard of hearing'), default=False)
    note_difficult_to_understand = models.BooleanField(_('Difficult to understand'), default=False)
    note_abusive_language = models.BooleanField(_('Abusive language'), default=False)

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4

    DAYS = [
        (MONDAY)_('Monday'),
        (TUESDAY)_('Tuesday'),
        (WEDNESDAY)_('Wednesday'),
        (THURSDAY)_('Thursday'),
        (FRIDAY)_('Friday'),
    ]

    availability_monday = models.ManyToManyField(
        TimeSlot, verbose_name=_('Monday'), blank=True, related_name='+')
    availability_tuesday = models.ManyToManyField(
        TimeSlot, verbose_name=_('Tuesday'), blank=True, related_name='+')
    availability_wednesday = models.ManyToManyField(
        TimeSlot, verbose_name=_('Wednesday'), blank=True, related_name='+')
    availability_thursday = models.ManyToManyField(
        TimeSlot, verbose_name=_('Thursday'), blank=True, related_name='+')
    availability_friday = models.ManyToManyField(
        TimeSlot, verbose_name=_('Friday'), blank=True, related_name='+')

    not_available_until = DateTimeField(_("not available until"), blank=True, null=True)

    class Meta:
        verbose_name = _('Subject')

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
        ]

    @cached_property
    def consent(self):
        try:
            return self.consentconfirmation_set.latest()
        except ConsentConfirmation.DoesNotExist:
            return None

    @cached_property
    def confirmed_consent(self):
        try:
            return self.consentconfirmation_set.filter(
                status=ConsentConfirmation.CONFIRMED
            ).latest()
        except ConsentConfirmation.DoesNotExist:
            return None

    @cached_property
    def is_complete(self):
        # these conditions are also checked in the form
        return self.consent or not Consent.objects.exists()

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

    def get_availability_monday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_monday.all())

    def get_availability_tuesday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_tuesday.all())

    def get_availability_wednesday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_wednesday.all())

    def get_availability_thursday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_thursday.all())

    def get_availability_friday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_friday.all())


class SubjectNote(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    content = models.CharField(_('Content'), max_length=128, blank=True)


class Consent(models.Model):
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    info = models.CharField(_('Info'), max_length=128)
    file = RestrictedFileField(
        _('File'),
        upload_to='consent/',
        content_types=['application/pdf'],
        max_upload_size=settings.CASTELLUM_FILE_UPLOAD_MAX_SIZE,
    )

    class Meta:
        get_latest_by = 'created_at'

    def __str__(self):
        return _('Version %i') % self.pk

    @cached_property
    def is_current(self):
        return not Consent.objects.filter(created_at__gt=self.created_at).exists()


class ConsentConfirmation(models.Model):
    WAITING = 'waiting'
    CONFIRMED = 'confirmed'

    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    revision = models.ForeignKey(Consent, on_delete=models.CASCADE)
    type = models.CharField(_('Type'), max_length=64, choices=[
        ('online', _('Online form')),
        ('paper', _('Pen & Paper')),
        ('phone', _('Telephone')),
    ])
    status = models.CharField(_('Status'), max_length=64, choices=[
        (WAITING, _('Waiting for confirmation')),
        (CONFIRMED, _('Confirmed')),
    ])

    class Meta:
        get_latest_by = 'revision__created_at'
        verbose_name = _('Consent confirmation')
