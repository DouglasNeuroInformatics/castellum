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

import math
import uuid

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

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
    TOOLTIPS = {
        'blocked': _('The subject has been blocked due to inappropriate behaviour.'),
        'deceased': _('The subject has passed away.'),
        'export_requested': _(
            'The subject wants to receive an export of all data we have stored about them.'
        ),
        'unnecessary_recruitment_data': _(
            'The subject does not have recruitment consent, so '
            'any data that is only relevant for recruitment should be deleted.'
        ),
        'to_be_deleted': _(
            'The subject wants all data about them to be deleted or fully anonymized.'
        ),
        'unreachable': _('There is no way to contact the subject.'),
        'no_legal_basis': _('There is no legal reason to keep the data of the subject.'),
    }

    uuid = models.UUIDField(_('UUID'), default=uuid.uuid4, primary_key=True)

    attributes = models.JSONField(_('Recruitment attributes'), encoder=DjangoJSONEncoder)
    study_type_disinterest = models.ManyToManyField(
        'studies.StudyType',
        verbose_name=_(
            'Does not want to participate or is permanently '
            'unsuitable for the following study types'
        ),
        blank=True,
        related_name='+',
    )

    privacy_level = models.FloatField(
        _('Privacy level'),
        help_text=_('Users need at least this level to access this subject'),
        default=0.0,
    )

    to_be_deleted = models.DateField(
        _('To be deleted'),
        blank=True,
        null=True,
        help_text=format_lazy(
            '{} {} {} {}',
            _('The subject wants all data about them to be deleted or fully anonymized.'),
            _(
                'This includes all data in Castellum and possibly all data collected in studies '
                '(if no other legal bases apply, for example retention periods).'
            ),
            _(
                'Furthermore, the subject has explicitly rejected the option to only withdraw '
                'recruitment consent instead.'
            ),
            _(
                'When a subject requests GDPR deletion please use this option to set the '
                'processing of their request in motion.'
            ),
        )
    )
    to_be_deleted_notified = models.BooleanField(default=False)

    export_requested = models.DateField(
        _('Export requested'),
        blank=True,
        null=True,
        help_text=format_lazy(
            '{} {} {}',
            _('The subject wants to receive an export of all data we have stored about them.'),
            _('This includes all data in Castellum and all data collected in studies.'),
            _(
                'When a subject requests GDPR export please use this option to set the '
                'processing of their request in motion.'
            ),
        ),
    )

    deceased = models.BooleanField(_('Subject is deceased'), default=False)

    blocked = models.BooleanField(_('Subject is blocked'), default=False, help_text=_(
        'The person has been blocked due to inappropriate behaviour. '
        'They will neither be considered for recruitment, nor contacted as a legal representative. '
        'Blocking this person does not automatically block any represented subjects nor '
        'co-representatives. They may thus still receive information about the recruitment '
        'process.'
    ))

    source = models.CharField(_('Data source'), max_length=128, blank=True)

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
        contact = Contact.objects.get(subject_uuid=self.uuid)
        contact.__dict__['subject'] = self
        return contact

    @cached_property
    def has_consent(self):
        from castellum.recruitment import filter_queries
        return Subject.objects.filter(
            filter_queries.has_consent(), pk=self.pk,
        ).exists()

    @cached_property
    def unknown_consent(self):
        return not Consent.objects.filter(subject=self).exists()

    @cached_property
    def has_consent_or_waiting(self):
        from castellum.recruitment import filter_queries
        return Subject.objects.filter(
            filter_queries.has_consent(include_waiting=True), pk=self.pk,
        ).exists()

    @property
    def has_consent_from_before_full_age(self):
        return (
            self.contact.is_underage is False
            and self.has_consent
            and self.consent.underage_when_given
        )

    @cached_property
    def consent_action_required(self):
        try:
            deprecated = self.consent.document.is_deprecated
        except AttributeError:
            deprecated = False

        return (
            self.has_consent_from_before_full_age
            or self.unknown_consent
            or deprecated
        )

    @cached_property
    def has_study_consent(self):
        from castellum.recruitment.models import Participation
        from castellum.studies.models import Study
        return (
            self.participation_set
            .exclude(status=Participation.UNSUITABLE)
            .exclude(
                study__status=Study.FINISHED,
                study__domains=None,
                news_interest=Participation.NOT_INTERESTED,
            )
            .exists()
        )

    @property
    def has_legal_basis(self):
        return (
            self.has_consent_or_waiting
            or self.has_study_consent
            or self.contact.is_legal_representative
            or (not self.deceased and self.blocked)
        )

    @cached_property
    def has_unnecessary_recruitment_data(self):
        # Needs to match ``data_protection.helpers.get_unnecessary_recruitment_data()``
        completed, _total = self.get_completeness()
        return not self.has_consent_or_waiting and (
            completed > (1 if settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID else 0)
            or self.study_type_disinterest.exists()
        )

    @property
    def is_available(self):
        now = timezone.localtime()
        return not self.not_available_until or self.not_available_until <= now

    def get_reliability_display(self):
        if not hasattr(self, 'reliability_issues'):
            annotated = Subject.objects.annotate_reliability().get(pk=self.pk)
            self.reliability_total = annotated.reliability_total
            self.reliability_issues = annotated.reliability_issues

        if self.reliability_total == 0:
            return _('no data so far')
        else:
            return _('{issues} issues in {total} studies').format(
                issues=self.reliability_issues, total=self.reliability_total
            )

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

    def get_effective_privacy_level(self):
        return math.ceil(self.privacy_level)


class ConsentDocument(models.Model):
    name = models.CharField(_('Name'), max_length=254, blank=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    is_deprecated = models.BooleanField(_('Is deprecated'), default=False)
    file = RestrictedFileField(
        _('File'),
        blank=True,
        upload_to='consent/',
        content_types=['application/pdf'],
        max_upload_size=settings.CASTELLUM_FILE_UPLOAD_MAX_SIZE,
    )

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.name or _('Version {}').format(self.pk)


class Consent(models.Model):
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    subject = models.OneToOneField(Subject, on_delete=models.CASCADE)
    underage_when_given = models.BooleanField(_('Underage when given'), null=True)
    document = models.ForeignKey(
        ConsentDocument,
        verbose_name=_('Document'),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    file = RestrictedFileField(
        _('Signed file'),
        blank=True,
        upload_to='subjects/consents/',
        content_types=['application/pdf'],
        max_upload_size=settings.CASTELLUM_FILE_UPLOAD_MAX_SIZE,
    )

    class Meta:
        verbose_name = _('Consent')

    def save(self, *args, **kwargs):
        # updates Subject.updated_at
        self.subject.save()
        return super().save(*args, **kwargs)


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
    delete_url = models.URLField(
        _('Delete URL'), max_length=128, blank=True, null=True, unique=True
    )
    source = models.CharField(_('Data source'), max_length=128, blank=True)
    data_is_deleted = models.BooleanField(
        _('Personal data has been deleted'),
        default=False,
    )

    @cached_property
    def contact(self):
        from castellum.contacts.models import ContactCreationRequest

        return ContactCreationRequest.objects.get(subject_id=self.pk)

    def mark_as_deleted(self):
        self.contact.delete()
        self.data_is_deleted = True
        self.save()

    def convert_to_real_subject(self):
        contact = self.contact.convert_to_real_contact()
        subject = contact.subject
        subject.source = self.source
        subject.save()
        # CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID is synced on contact save
        contact.save()
        return subject
