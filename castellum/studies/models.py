# (c) 2018-2023 MPIB <https://www.mpib-berlin.mpg.de/>,
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
import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel
from parler.models import TranslatedFields

from castellum.castellum_auth.models import User
from castellum.pseudonyms.models import Domain
from castellum.utils.fields import ColorField
from castellum.utils.fields import DateField
from castellum.utils.fields import PhoneNumberField
from castellum.utils.fields import RestrictedFileField
from castellum.utils.forms import JsonFileValidator

APP_DIR = Path(__file__).resolve().parent
with open(APP_DIR / 'schemas' / 'geojson.json') as fh:
    GEOJSON_SCHEMA = json.load(fh)


def geofilter_upload_to(instance, filename):
    assert instance.pk
    return f'studies/{instance.pk}/geofilters/{filename}'


def consent_upload_to(instance, filename):
    assert instance.pk
    return f'studies/{instance.pk}/consents/{filename}'


class StudyType(TranslatableModel):
    # see also schemas/study.json
    EXPORT_KEYS = 'Online', 'Behavioral lab', 'MRI', 'Simulation', 'EEG'

    translations = TranslatedFields(
        label=models.CharField(_('Label'), max_length=64),
    )
    exclusion_criteria = models.TextField(
        _(
            'Additional subject characteristics that should be verified during '
            'recruitment'
        ),
        blank=True,
    )
    export_key = models.CharField(
        _('Export key'),
        max_length=32,
        choices=[(k, k) for k in EXPORT_KEYS],
        blank=True,
    )

    def __str__(self):
        return self.label


class Study(models.Model):
    EDIT = 0
    EXECUTION = 1
    FINISHED = 2

    STATUS = [
        (EDIT, _('Edit')),
        (EXECUTION, _('Execution')),
        (FINISHED, _('Finished')),
    ]

    name = models.CharField(_('Name'), max_length=254, unique=True)
    contact_person = models.CharField(_('Contact person'), max_length=254)
    email = models.EmailField(_('E-mail-address'), max_length=128)
    phone = PhoneNumberField(_('Phone number'), max_length=32)

    principal_investigator = models.CharField(
        _('Principal Investigator'), max_length=254, blank=True
    )
    affiliated_scientists = models.CharField(
        _('Affiliated Scientists'), max_length=254, blank=True
    )
    affiliated_research_assistants = models.CharField(
        _('Affiliated Research Assistants'), max_length=254, blank=True
    )
    description = models.TextField(_('Description'), blank=True)
    url = models.URLField(_('URL'), blank=True)

    previous_status = models.SmallIntegerField(
        _('Previous status'), choices=STATUS, default=EDIT
    )
    status = models.SmallIntegerField(_('Status'), choices=STATUS, default=EDIT)
    min_subject_count = models.PositiveIntegerField(
        _('Required number of subjects'), default=0
    )
    session_instructions = models.TextField(
        _('Session instructions'),
        help_text=_(
            'Please describe any requirements for carrying out the sessions listed '
            'below. For example, specify time intervals between sessions that need to '
            'be considered for booking appointments.'
        ),
        blank=True,
    )
    sessions_start = DateField(_('Start of test sessions'), blank=True, null=True)
    sessions_end = DateField(_('End of test sessions'), blank=True, null=True)
    recruitment_text = models.TextField(
        _('Recruitment text'),
        help_text=_(
            'This text will be used during recruitment dialogue. Thus, please describe '
            'the study from the perspective of recruiters and potential participants: '
            'What is it about? How long will it take? Are there any potential benefits '
            'or risks for participants? If applicable, also present the amount of '
            'expense allowance and related requirements.'
        ),
        blank=True,
    )

    members = models.ManyToManyField(User, through='StudyMembership')
    domains = GenericRelation(Domain)
    general_domains = models.ManyToManyField(
        Domain,
        verbose_name=_('General pseudonym domains'),
        blank=True,
        limit_choices_to={'object_id': None},
    )
    advanced_filtering = models.BooleanField(
        _('Advanced filtering'),
        help_text=_(
            'By default you can create only one filtergroup in which all the filters '
            'are joined by AND operator. Advanced filtering allows you to create '
            'multiple filtergroups which are joined by OR operator.'
        ),
        default=False,
    )
    geo_filter = RestrictedFileField(
        _('Geo filter file'),
        help_text=_(
            'A GeoJSON file that contains (multi)polygons. Only subjects who live '
            'inside the polygons will be considered for this study.'
        ),
        blank=True,
        upload_to=geofilter_upload_to,
        content_types=['application/json'],
        max_upload_size=settings.CASTELLUM_FILE_UPLOAD_MAX_SIZE,
        validators=[JsonFileValidator(GEOJSON_SCHEMA, '#/$defs/geofilter')],
    )
    is_exclusive = models.BooleanField(
        _('Exclusive subjects'),
        help_text=_(
            'When set, this ensures that potential subjects for this study will not '
            'be recruited in other studies. Please note that this may hinder other '
            'researchers in finding enough participants.'
        ),
        default=False,
    )
    complete_matches_only = models.BooleanField(
        _('Complete filter matches only'),
        help_text=_(
            'By default, filters may include subjects with incomplete attributes. '
            'This feature is supposed to improve the quality of the database by '
            'asking recruiters to fill missing values on the go. Only allowing '
            'complete filter matches can speed up individual recruitments but may '
            'deteriorate the quality of the database as a whole. Furthermore, this '
            'reduces the number of potential subjects.'
        ),
        default=False,
    )
    excluded_studies = models.ManyToManyField(
        'studies.Study',
        verbose_name=_('Excluded studies'),
        related_name='+',
        blank=True,
    )

    is_filter_trial = models.BooleanField(
        _('Is a filter trial'),
        help_text=_(
            'Use this if you only want to see how many subjects would match a specific '
            'study and filter configuration without actually intending to recruit.'
        ),
        default=False,
    )

    consent = RestrictedFileField(
        _('Study consent'),
        help_text=_(
            'A blueprint of the study consent. This file can be obtained '
            '(and printed) later by recruiters or conductors.'
        ),
        blank=True,
        upload_to=consent_upload_to,
        content_types=['application/pdf'],
        max_upload_size=settings.CASTELLUM_FILE_UPLOAD_MAX_SIZE,
    )

    exportable_attributes = models.ManyToManyField(
        'recruitment.AttributeDescription',
        verbose_name=_('Exportable recruitment attributes'),
        help_text=_(
            'This allows to download these attributes as a data file in study '
            'execution, e.g. to use a specific attribute for the analysis.'
        ),
        related_name='+',
        blank=True,
    )

    mail_subject = models.CharField(_('E-mail subject'), max_length=254, blank=True)
    mail_body = models.TextField(
        _('E-mail body'),
        help_text=_(
            'Any "{name}"-tags included in the e-mail-body will '
            'automatically be replaced with the full name of the subject.'
        ),
        blank=True,
    )

    class Meta:
        ordering = ['name']
        permissions = [
            ('access_study', _('Can access studies')),
            ('approve_study', _('Can approve studies')),
        ]

    def __str__(self):
        return self.name

    def set_status(self, status):
        self.previous_status = self.status
        self.status = status
        self.save()

    def restore_previous_status(self):
        self.set_status(self.previous_status)

    def clean(self):
        if (
            self.pk
            and not self.advanced_filtering
            and self.subjectfiltergroup_set.count() > 1
        ):
            raise ValidationError(
                _(
                    "Studies with more than one filtergroup can't be transformed back "
                    'to basic filtering. Delete all but one filtergroup first!'
                ),
                code='invalid',
            )

        mailfields = [self.mail_subject, self.mail_body]
        if any(mailfields) and not all(mailfields):
            raise ValidationError(
                _(
                    'Mail settings have to be filled out completely if you wish to use '
                    'this feature.'
                ),
                code='invalid',
            )

    def get_invited_max_privacy_level(self):
        from castellum.recruitment.models import Participation

        key = 'subject__privacy_level'
        result = (
            self.participation_set
            .filter(status=Participation.INVITED)
            .aggregate(models.Max(key))
        )
        return result[key + '__max'] or 0

    @cached_property
    def members_max_privacy_level(self):
        members = set(self.recruiters + self.conductors)
        return max([user.get_privacy_level() for user in members], default=2)

    @cached_property
    def members_min_privacy_level(self):
        members = set(self.recruiters + self.conductors)
        return min([user.get_privacy_level() for user in members], default=2)

    @property
    def study_type(self):
        return StudyType.objects.filter(studysession__study=self).distinct()

    @property
    def followup_urgent(self):
        today = datetime.date.today()
        return self.participation_set.filter(followup_date__lte=today).exists()

    @property
    def tags(self):
        return self.studytag_set.values_list('name', flat=True)

    @cached_property
    def has_filters(self):
        from castellum.recruitment.models import SubjectFilter
        return SubjectFilter.objects.filter(group__study=self).exists()

    @cached_property
    def has_exclusion_criteria(self):
        return (
            settings.CASTELLUM_GENERAL_RECRUITMENT_TEXT
            or self.recruitment_text
            or self.study_type.exclude(exclusion_criteria='').exists()
        )

    @cached_property
    def invited_count(self):
        from castellum.recruitment.models import Participation
        return self.participation_set.filter(status=Participation.INVITED).count()

    @property
    def is_started(self):
        if self.status == Study.FINISHED:
            return self.previous_status == Study.EXECUTION
        else:
            return self.status == Study.EXECUTION

    # NOTE: this might not be the same as the group of the same name!
    @cached_property
    def recruiters(self):
        recruiters = []
        for user in self.members.all():
            if user.has_perm('recruitment.recruit', obj=self):
                recruiters.append(user)
        return recruiters

    @cached_property
    def conductors(self):
        conductors = []
        for user in self.members.all():
            if user.has_perm('recruitment.conduct_study', obj=self):
                conductors.append(user)
        return conductors

    def export(self):
        status_map = {
            Study.EDIT: 'not_started',
            Study.EXECUTION: 'started',
            Study.FINISHED: 'finished',
        }

        data = {
            'name': self.name,
            'contact_person': {
                'name': self.contact_person,
                'email': self.email,
            },
            'description': self.description,
            'status': status_map[self.status],
            'sessions_start': self.sessions_start,
            'sessions_end': self.sessions_end,
            'number_participants_expected': self.min_subject_count,
            'keywords': list(self.tags),
            'type': [
                t for t in self.study_type.values_list('export_key', flat=True) if t
            ],
            'members': [{
                'username': user.username,
                'name': user.get_full_name()[:128],
                'email': user.email,
            } for user in self.members.all()],
        }

        if self.principal_investigator:
            data['principal_investigator'] = {'name': self.principal_investigator}

        return data


class StudyGroup(models.Model):
    name = models.CharField(_('name'), max_length=150, unique=True)
    permissions = models.ManyToManyField(
        Permission, verbose_name=_('permissions'), blank=True
    )

    def __str__(self):
        return self.name


class StudyMembership(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField(StudyGroup, blank=True, related_name='+')

    class Meta:
        unique_together = ['study', 'user']

    def __str__(self):
        return str(self.user)


class Resource(models.Model):
    name = models.CharField(_('Name'), max_length=128)
    managers = models.ManyToManyField(User, verbose_name=_('Managers'), blank=True)
    url = models.URLField(
        _('URL'),
        help_text=_(
            'Any "{start}"- and "{end}-tags included in the URL will '
            'automatically be replaced by the relevant datetime in ISO 8601 format.'
        ),
        blank=True,
    )
    color = ColorField(_('Color'), default='#000000')

    def __str__(self):
        return self.name


class StudySession(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=128)
    duration = models.PositiveIntegerField(_('Duration of a session in minutes'))
    type = models.ManyToManyField(StudyType, verbose_name=_('Type'), blank=True)
    resources = models.ManyToManyField(
        Resource, verbose_name=_('Resources'), blank=True
    )
    domains = GenericRelation(Domain)
    reminders_enabled = models.BooleanField(_('Enable reminder emails'), default=True)
    reminder_text = models.TextField(
        _('Additional text for reminder emails'), blank=True
    )
    schedule_id = models.CharField(
        _('External schedule ID'), max_length=64, blank=True, null=True, unique=True
    )
    schedule_updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.study} - {self.name}'

    @property
    def domain(self):
        domain = self.domains.first()
        if domain:
            return domain.key


class StudyTag(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=128)

    def __str__(self):
        return self.name
