# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
import math
import uuid

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from castellum.castellum_auth.models import User
from castellum.utils.fields import DateTimeField
from castellum.utils.fields import RestrictedFileField
from castellum.utils.models import TimeStampedModel


class SubjectQuerySet(models.QuerySet):
    def annotate_reliability(self):
        return self.annotate(
            reliability_total=models.Count('reliabilityentry'),
            reliability_issues=models.Count(
                'reliabilityentry',
                filter=models.Q(reliabilityentry__was_reliable=False),
            ),
        )


class Subject(TimeStampedModel):
    TOOLTIPS = {
        'blocked': _('The subject has been blocked due to inappropriate behaviour.'),
        'deceased': _('The subject has passed away.'),
        'export_requested': _(
            'The subject wants to receive an export of all data we have '
            'stored about them.'
        ),
        'unnecessary_recruitment_data': _(
            'The subject does not have recruitment consent, so '
            'any data that is only relevant for recruitment should be deleted.'
        ),
        'to_be_deleted': _(
            'The subject wants all data about them to be deleted or fully anonymized.'
        ),
        'unreachable': _('There is no way to contact the subject.'),
        'no_legal_basis': _(
            'There is no legal reason to keep the data of the subject.'
        ),
    }

    uuid = models.UUIDField(_('UUID'), default=uuid.uuid4, primary_key=True)

    attributes = models.JSONField(
        _('Recruitment attributes'), encoder=DjangoJSONEncoder
    )
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
            _(
                'The subject wants all data about them to be deleted or fully '
                'anonymized.'
            ),
            _(
                'This includes all data in Castellum and possibly all data collected '
                'in studies (if no other legal bases apply, for example retention '
                'periods).'
            ),
            _(
                'Furthermore, the subject has explicitly rejected the option to only '
                'withdraw recruitment consent instead.'
            ),
            _(
                'When a subject requests GDPR deletion please use this option to set '
                'the processing of their request in motion.'
            ),
        ),
    )
    to_be_deleted_notified = models.BooleanField(default=False)

    export_requested = models.DateField(
        _('Export requested'),
        blank=True,
        null=True,
        help_text=format_lazy(
            '{} {} {}',
            _(
                'The subject wants to receive an export of all data we have stored '
                'about them.'
            ),
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
        'They will neither be considered for recruitment, nor contacted as a legal '
        'representative. Blocking this person does not automatically block any '
        'represented subjects nor co-representatives. They may thus still receive '
        'information about the recruitment process.'
    ))

    source = models.CharField(_('Data source'), max_length=128, blank=True)

    not_available_until = DateTimeField(_('not available until'), blank=True, null=True)

    objects = SubjectQuerySet.as_manager()

    class Meta:
        verbose_name = _('Subject')
        permissions = [
            ('export_subject', _('Can export all data related to a subject')),
            ('view_audit_trail', _('Can view audit trail')),
            ('add_to_study', _('Can add subject to a study without checking filters')),
            ('list_participations', _('Can list all study participations')),
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
        return (
            not self.has_consent
            and not Consent.objects.filter(subject=self, document=None).exists()
        )

    @cached_property
    def has_consent_with_ineffective(self):
        from castellum.recruitment import filter_queries
        return Subject.objects.filter(
            filter_queries.has_consent(include_ineffective=True), pk=self.pk,
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
        return (
            self.has_consent_from_before_full_age
            or self.unknown_consent
            or (self.has_consent and self.consent.expire_soon)
            or (self.has_consent and self.consent.document.is_deprecated)
        )

    @cached_property
    def has_study_consent(self):
        from castellum.recruitment.models import Participation
        from castellum.studies.models import Study
        q_news_interest = (
            models.Q(news_interest=Participation.NOT_INTERESTED)
            | models.Q(study__updated_at__lt=(
                datetime.date.today() - settings.CASTELLUM_STUDY_NEWS_PERIOD
            ))
        )
        return (
            self.participation_set
            .filter(status__in=Participation.INVITED_SET)
            .exclude(
                q_news_interest,
                study__status=Study.FINISHED,
            )
            .exists()
        )

    @property
    def has_legal_basis(self):
        return (
            self.has_consent
            or self.has_study_consent
            or self.contact.is_legal_representative
            or (not self.deceased and self.blocked)
        )

    @cached_property
    def has_unnecessary_recruitment_data(self):
        from castellum.data_protection.helpers import get_unnecessary_recruitment_data
        return get_unnecessary_recruitment_data().filter(pk=self.pk).exists()

    @cached_property
    def has_missing_attributes(self):
        from castellum.recruitment import filter_queries
        qs = Subject.objects.filter(pk=self.pk)
        qs = filter_queries.get_has_missing_attributes(qs)
        return qs.exists()

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

    def get_privacy_level_display(self):
        options = [
            (0.0, _('0 (regular)')),
            (1.0, _('1 (increased)')),
            (2.0, _('2 (high)')),
            *settings.CASTELLUM_CUSTOM_PRIVACY_LEVELS,
        ]
        return dict(options).get(self.privacy_level)

    def get_effective_privacy_level(self):
        return math.ceil(self.privacy_level)

    @property
    def date_of_birth(self):
        if settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID:
            key = f'd{settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID}'
            value = self.attributes.get(key)
            try:
                return datetime.date.fromisoformat(value)
            except ValueError:
                return None


class ConsentDocument(models.Model):
    name = models.CharField(_('Name'), max_length=254, blank=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    is_valid = models.BooleanField(_('Is valid'), default=True)
    is_deprecated = models.BooleanField(_('Is deprecated'), default=False)
    expire_after = models.DurationField(_('Expire after'), blank=True, null=True)
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


def consent_upload_to(instance, filename):
    subject = instance.subject
    assert subject.pk
    return f'subjects/{subject.pk}/consents/{filename}'


class BaseConsent(models.Model):
    underage_when_given = models.BooleanField(_('Underage when given'), null=True)
    document = models.ForeignKey(
        ConsentDocument,
        limit_choices_to={'is_valid': True},
        verbose_name=_('Document'),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    file = RestrictedFileField(
        _('Signed file'),
        blank=True,
        upload_to=consent_upload_to,
        max_length=140,
        content_types=['application/pdf'],
        max_upload_size=settings.CASTELLUM_FILE_UPLOAD_MAX_SIZE,
    )

    # only relevant if document=None
    excluded_by_us = models.BooleanField(_('Excluded by us'), default=False)

    class Meta:
        abstract = True


class Consent(BaseConsent):
    subject = models.OneToOneField(Subject, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    full_age_notified_1 = models.BooleanField(
        _('First full age expiration notification sent'), default=False
    )
    full_age_notified_2 = models.BooleanField(
        _('Second full age expiration notification sent'), default=False
    )
    expire_at_notified = models.BooleanField(
        _('Expiration notification sent'), default=False
    )

    class Meta:
        verbose_name = _('Consent')

    @property
    def expire_at(self):
        if self.document and self.document.expire_after:
            return self.updated_at + self.document.expire_after

    @property
    def expire_soon(self):
        threshold = timezone.now() - settings.CASTELLUM_EXPIRE_AT_WARN_BEFORE
        return self.expire_at and self.expire_at > threshold

    def save(self, *args, **kwargs):
        # updates Subject.updated_at
        self.subject.save()

        ConsentRevision.objects.create(
            subject=self.subject,
            underage_when_given=self.underage_when_given,
            excluded_by_us=self.excluded_by_us,
            document=self.document,
            file=self.file,
        )

        return super().save(*args, **kwargs)


class ConsentRevision(BaseConsent):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    @property
    def expire_at(self):
        if self.document and self.document.expire_after:
            return self.created_at + self.document.expire_after

    class Meta:
        verbose_name = _('Consent revision')
        verbose_name_plural = _('Consent revisions')
        ordering = ['created_at']


class ExportAnswer(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created_at = models.DateField(_('Created at'), auto_now_add=True)
    created_by = models.CharField(_('Created by'), max_length=150)

    class Meta:
        verbose_name = _('Export answer')
        verbose_name_plural = _('Export answers')

    def __str__(self):
        return str(self.created_at)


class Report(models.Model):
    # - A subject is blocked immediately when a report is created to protect employees.
    # - Reviewers can decide to revert a block. They can also take action against users
    #   who abuse the report feature.
    # - The report is deleted when the reviewers make their decision.
    # - It is not possible to report an already blocked subject. Otherwise reviewers
    #   might revert a block based on a bogus report even if there had previously been a
    #   legitimate report.
    # - The report is kept even if the user has been deleted so reviewers can still make
    #   a decision.
    # - The report is kept even if the subject has been deleted so reviewers can still
    #   offer support.
    subject = models.ForeignKey(
        Subject, verbose_name=_('Subject'), on_delete=models.SET_NULL, null=True
    )
    user = models.ForeignKey(
        User, verbose_name=_('User'), on_delete=models.SET_NULL, null=True
    )
    additional_wishes = models.TextField(
        _('Additional wishes (optional)'),
        help_text=_('e.g. Request for a confidential conversation'),
        blank=True,
    )


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
        # We keep the source/delete_url so import scripts can ignore duplicates.
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
