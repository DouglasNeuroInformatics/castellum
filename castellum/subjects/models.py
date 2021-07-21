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

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from dateutil.relativedelta import relativedelta

from castellum.utils import uuid_str
from castellum.utils.fields import DateTimeField
from castellum.utils.fields import RestrictedFileField
from castellum.utils.models import TimeStampedModel


class SubjectQuerySet(models.QuerySet):
    def annotate_reliability(self):
        return self.annotate(
            reliability_total=models.Count('reliabilityentry'),
            reliability_issues=models.Count(
                'reliabilityentry', filter=models.Q(reliabilityentry__was_reliable=False)
            ),
        )


class Subject(TimeStampedModel):
    slug = models.CharField(_('Slug'), max_length=64, default=uuid_str, unique=True)

    attributes = models.JSONField(_('Recruitment attributes'), encoder=DjangoJSONEncoder)
    onetime_invitation_disinterest = models.BooleanField(
        _('Does not want to participate in one time invitations'),
        default=False,
    )
    study_type_disinterest = models.ManyToManyField(
        'studies.StudyType',
        verbose_name=_('Does not want to participate in the following study types'),
        blank=True,
        related_name='+',
    )

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

    deceased = models.BooleanField(_('Subject is deceased'), default=False)

    blocked = models.BooleanField(_('Subject is blocked'), default=False, help_text=_(
        'The subject has been blocked due to inappropriate behaviour. '
        'They will neither be considered for recruitment, nor contacted as guardians. '
        'Blocking this subject does not automatically block their ward nor their '
        'co-guardians. They may thus still receive information about the recruitment '
        'process of their wards.'
    ))

    source = models.CharField(_('Data source'), max_length=128, blank=True)

    additional_suitability_document = models.ManyToManyField(
        'studies.StudyType',
        verbose_name=_('Additional suitability document for study type'),
        related_name='+',
        help_text=_(
            'Additional suitability documents are records that certify that a subject may safely '
            'undergo all types of exams or tests conducted in the respective type of study.'
        ),
        blank=True,
    )

    not_available_until = DateTimeField(_("not available until"), blank=True, null=True)

    objects = SubjectQuerySet.as_manager()

    class Meta:
        verbose_name = _('Subject')
        permissions = [
            ('export_subject', _('Can export all data related to a subject')),
        ]

    def delete(self):
        self.contact.delete()
        return super().delete()

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
        return (
            self.has_consent_or_waiting
            or self.has_study_consent
            or self.contact.is_guardian
            or self.blocked
        )

    @property
    def is_available(self):
        now = timezone.localtime()
        return not self.not_available_until or self.not_available_until <= now

    def annotate_reliability(self):
        if hasattr(self, 'reliability_issues'):
            return

        annotated = Subject.objects.annotate_reliability().get(pk=self.pk)
        self.reliability_total = annotated.reliability_total
        self.reliability_issues = annotated.reliability_issues

    def get_data(self):
        from castellum.recruitment.models import AttributeDescription

        qs = AttributeDescription.objects.all()
        return {desc.json_key: self.attributes.get(desc.json_key) for desc in qs}

    def get_completeness(self):
        from castellum.recruitment.models import AttributeDescription

        # Needs to match ``filter_queries.completeness_expr()``
        completed = len([k for k, v in self.attributes.items() if v not in [None, '']])
        total = AttributeDescription.objects.count()
        return completed, total


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
        return _('Version {}').format(self.pk)


class Consent(models.Model):
    WAITING = 'waiting'
    CONFIRMED = 'confirmed'

    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    subject = models.OneToOneField(Subject, on_delete=models.CASCADE)
    document = models.ForeignKey(
        ConsentDocument, verbose_name=_('Document'), on_delete=models.CASCADE
    )
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
        verbose_name_plural = _('Export answers')

    def __str__(self):
        return str(self.created_at)


class SubjectCreationRequest(TimeStampedModel):
    external_id = models.IntegerField(_('External ID'), blank=True, null=True, unique=True)
    source = models.CharField(_('Data source'), max_length=128, blank=True)

    @cached_property
    def contact(self):
        from castellum.contacts.models import ContactCreationRequest
        return ContactCreationRequest.objects.get(subject_id=self.pk)

    def delete(self):
        self.contact.delete()
        return super().delete()

    def convert_to_real_subject(self):
        contact = self.contact.convert_to_real_contact()
        subject = contact.subject
        subject.source = self.source
        subject.save()
        return subject
