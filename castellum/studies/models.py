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
import json
import os

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.forms import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from parler.models import TranslatableModel
from parler.models import TranslatedFields

from castellum.castellum_auth.models import User
from castellum.pseudonyms.helpers import create_domain
from castellum.pseudonyms.helpers import delete_domain
from castellum.utils.fields import DateField
from castellum.utils.fields import RestrictedFileField
from castellum.utils.forms import JsonFileValidator

APP_DIR = os.path.dirname(__file__)
GEOJSON_SCHEMA = json.load(open(os.path.join(APP_DIR, 'schemas', 'geojson.json')))


class StudyType(TranslatableModel):
    # see also schemas/study.json
    EXPORT_KEYS = 'Online', 'Behavioral lab', 'MRI', 'Simulation', 'EEG'

    translations = TranslatedFields(
        label=models.CharField(_('Label'), max_length=64),
    )
    exclusion_criteria = models.TextField(
        _('Additional subject characteristics that should be verified during recruitment'),
        blank=True,
    )
    data_sensitivity = models.BooleanField(_('Contains sensitive data'), default=False)
    export_key = models.CharField(
        _('Export key'), max_length=32, choices=[(k, k) for k in EXPORT_KEYS], blank=True
    )

    def __str__(self):
        return self.label


class StudyTypeEventFeed(models.Model):
    study_type = models.ForeignKey(StudyType, on_delete=models.CASCADE)
    url = models.URLField(_('URL'))

    def __str__(self):
        return '%s %s' % (self.study_type, self.url)


class Study(models.Model):
    EDIT = 0
    EXECUTION = 1
    FINISHED = 2

    STATUS = [
        (EDIT, _('Edit')),
        (EXECUTION, _('Execution')),
        (FINISHED, _('Finished')),
    ]

    name = models.CharField(_('Name'), max_length=254)
    contact_person = models.CharField(_('Responsible contact person'), max_length=254)
    principal_investigator = models.CharField(_('Principal Investigator'), max_length=254)
    affiliated_scientists = models.CharField(_('Affiliated Scientists'), max_length=254, blank=True)
    affiliated_research_assistants = models.CharField(
        _('Affiliated Research Assistants'), max_length=254, blank=True
    )
    description = models.TextField(_('Description'), blank=True)
    keywords = models.CharField(_('Keywords'), max_length=254, blank=True)
    previous_status = models.SmallIntegerField(
        _('Previous status'), choices=STATUS, default=EDIT
    )
    status = models.SmallIntegerField(_('Status'), choices=STATUS, default=EDIT)
    data_sensitivity = models.BooleanField(_('Contains sensitive data'), default=False)
    min_subject_count = models.PositiveIntegerField(_('Required number of subjects'), default=0)
    session_instructions = models.TextField(
        _('Session instructions'),
        help_text=_(
            'Please describe any requirements for carrying out the sessions listed below. '
            'For example, specify time intervals between sessions that need to be '
            'considered for booking appointments.'
        ),
        blank=True,
    )
    sessions_start = DateField(_('Start of test sessions'), blank=True, null=True)
    sessions_end = DateField(_('End of test sessions'), blank=True, null=True)
    exclusion_criteria = models.TextField(
        _('Additional subject characteristics that should be verified during recruitment'),
        blank=True,
    )
    recruitment_text = models.TextField(
        _('Recruitment text'),
        help_text=_(
            'This text will be used during recruitment dialogue. Thus, please describe the study '
            'from the perspective of recruiters and potential participants: What is it about? '
            'How long will it take? Are there any potential benefits or risks for participants? '
            'If applicable, also present the amount of expense allowance and related requirements.'
        ),
        blank=True,
    )
    to_be_deleted_notified = models.BooleanField(default=False)

    members = models.ManyToManyField(User, through='StudyMembership')
    domain = models.CharField(max_length=64, unique=True, editable=False, default=None)
    advanced_filtering = models.BooleanField(
        _('Advanced filtering'),
        help_text=_(
            'By default you can create only one filtergroup in which all the filters are joined by '
            'AND operator. Advanced filtering allows you to create multiple filtergroups which are '
            'joined by OR operator.'
        ),
        default=False,
    )
    custom_filter = models.CharField(_('Custom filter'), max_length=254, blank=True)
    geo_filter = RestrictedFileField(
        _('Geo filter file'),
        help_text=_(
            'A GeoJSON file that contains only a single (multi)polygon. '
            'Only subjects who live inside this polygon will be considered for this study.'
        ),
        blank=True,
        upload_to='studies/geofilters/',
        content_types=['application/json', 'text/plain'],
        max_upload_size=settings.CASTELLUM_FILE_UPLOAD_MAX_SIZE,
        validators=[JsonFileValidator(GEOJSON_SCHEMA, '#/$defs/Feature')],
    )
    is_exclusive = models.BooleanField(
        _('Exclusive subjects'),
        help_text=_(
            'When set, this ensures that potential subjects for this study will not be recruited '
            'in other studies. Please note that this may hinder other researchers in finding '
            'enough participants.'
        ),
        default=False,
    )
    complete_matches_only = models.BooleanField(
        _('Complete filter matches only'),
        help_text=_(
            'By default, filters may include subjects with incomplete attribute sets. This feature '
            'is supposed to improve the quality of the database by asking recruiters to fill '
            'missing values on the go. Only allowing complete filter matches can speed up '
            'individual recruitments but may deteriorate the quality of the database as a whole. '
            'Furthermore, this reduces the number of potential subjects.'
        ),
        default=False,
    )
    excluded_studies = models.ManyToManyField(
        'studies.Study', verbose_name=_('Excluded studies'), related_name='+', blank=True
    )

    is_onetime_invitation = models.BooleanField(
        _('Is a one time invitation'),
        help_text=_(
            'Use this if you want to bypass the usual recruitment workflow and just send an '
            'email to subjects, e.g. to invite them to an anonymous online survey.'
        ),
        default=False
    )

    consent = RestrictedFileField(
        _('Consent'),
        blank=True,
        upload_to='studies/consent/',
        content_types=['application/pdf'],
        max_upload_size=settings.CASTELLUM_FILE_UPLOAD_MAX_SIZE,
    )

    mail_subject = models.CharField(_('E-mail subject'), max_length=254, blank=True)
    mail_body = models.TextField(
        _('E-mail body'),
        help_text=_(
            'Any "{firstname}" and "{lastname}"-tags included in the e-mail-body will '
            'automatically be replaced with the first and last name of the subject.'
        ),
        blank=True,
    )
    mail_reply_address = models.EmailField(_('Reply e-mail-address'), max_length=128, blank=True)

    class Meta:
        ordering = ['name']
        permissions = (
            ('access_study', _('Can access studies')),
        )

    def __str__(self):
        return self.name

    def restore_previous_status(self):
        self.status = self.previous_status
        self.save()

    def set_status(self, status):
        self.previous_status = self.status
        self.status = status
        self.save()

    def clean(self):
        if self.subjectfiltergroup_set.count() > 1 and not self.advanced_filtering:
            raise ValidationError(
                _(
                    'Studies with more than one filtergroup can\'t be transformed back to basic '
                    'filtering. Delete all but one filtergroup first!'
                ),
                code='invalid',
            )

        mailfields = [self.mail_subject, self.mail_body, self.mail_reply_address]
        if any(mailfields) and not all(mailfields):
            raise ValidationError(
                _(
                    'Mail settings have to be filled out completely if you wish to use '
                    'this feature.'
                ),
                code='invalid',
            )

    def save(self, *args, **kwargs):
        if not self.domain:
            self.domain = create_domain(settings.CASTELLUM_STUDY_DOMAIN_BITS)
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.domain:
            delete_domain(self.domain)
        return super().delete(*args, **kwargs)

    def get_filter_max_privacy_level(self):
        key = 'subjectfilter__description__privacy_level_read'
        result = self.subjectfiltergroup_set.aggregate(models.Max(key))
        return result[key + '__max'] or 0

    @property
    def study_type(self):
        return StudyType.objects.filter(studysession__study=self).distinct()

    @property
    def followup_urgent(self):
        today = datetime.date.today()
        return self.participation_set.filter(followup_date__lte=today).exists()

    @cached_property
    def has_filters(self):
        from castellum.recruitment.models import SubjectFilter
        return SubjectFilter.objects.filter(group__study=self).exists()

    @cached_property
    def has_exclusion_criteria(self):
        return (
            settings.CASTELLUM_GENERAL_EXCLUSION_CRITERIA or
            self.exclusion_criteria or
            self.study_type.exclude(exclusion_criteria='').exists()
        )

    @cached_property
    def is_sensitive(self):
        return self.data_sensitivity or self.study_type.filter(data_sensitivity=True).exists()

    # NOTE: this might not be the same as the group of the same name!
    @cached_property
    def recruiters(self):
        recruiters = []
        for user in self.members.all():
            if user.has_perm('recruitment.recruit', obj=self):
                recruiters.append(user)
        return recruiters

    def has_missing_values(self):
        return not all([
            self.principal_investigator,
            self.study_type.exists(),
            self.sessions_start,
            self.sessions_end,
            self.consent,
            self.recruiters,
            self.recruitment_text,
            self.has_filters,
        ])


class StudyMembership(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, blank=True, related_name='+')

    class Meta:
        unique_together = ('study', 'user')

    def __str__(self):
        return '{}:{}'.format(self.study, self.user)


class Resource(models.Model):
    name = models.CharField(_('Name'), max_length=128)

    def __str__(self):
        return self.name


class StudySession(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=128)
    duration = models.PositiveIntegerField(_('Duration of a session in minutes'))
    type = models.ManyToManyField(StudyType, verbose_name=_('Type'), blank=True)
    resource = models.ForeignKey(
        Resource, on_delete=models.SET_NULL, verbose_name=_('Resource'), blank=True, null=True
    )

    def __str__(self):
        return '{} - {}'.format(self.study, self.name)
