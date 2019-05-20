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

import datetime
import uuid

from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import models
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from castellum.castellum_auth.models import User
from castellum.utils.fields import DateField
from castellum.utils.fields import RestrictedFileField


class Study(models.Model):
    ONLINE = 0
    BEHAVIORAL_LAB = 1
    FMRI = 2
    SIMULATION = 3
    EEG = 4
    THIRD_PARTY = 5

    STUDY_TYPES = [
        (ONLINE, _('Online')),
        (BEHAVIORAL_LAB, _('Behavioral lab')),
        (FMRI, _('FMRI')),
        (SIMULATION, _('Simulation')),
        (EEG, _('EEG')),
        (THIRD_PARTY, _('3rd Party')),
    ]

    name = models.CharField(_('name'), max_length=254)
    contact_person = models.CharField(_('responsible contact person'), max_length=512)
    principal_investigator = models.CharField(
        _('Principal Investigator'), max_length=254, blank=True)
    affiliated_scientists = models.CharField(_('Affiliated Scientists'), max_length=254, blank=True)
    affiliated_research_assistants = models.CharField(
        _('Affiliated Research Assistants'), max_length=254, blank=True)
    description = models.TextField(_('description'), blank=True)
    keywords = models.CharField(_('keywords'), max_length=254, blank=True)
    study_type = models.IntegerField(
        _('Type of study'), choices=STUDY_TYPES, null=True)
    data_sensitivity = models.BooleanField(_('Contains sensitive data'), default=False)
    min_subjects_count = models.PositiveIntegerField(_('required number of subjects'),
                                                     blank=True,
                                                     default=0)
    expense_allowance = models.PositiveIntegerField(_('expense allowance'), blank=True, null=True)
    sessions_start = DateField(_('start of test sessions'), blank=True, null=True)
    sessions_end = DateField(_('end of test sessions'), blank=True, null=True)
    exclusion_criteria = models.TextField(_('Exclusion criteria'), blank=True)

    members = models.ManyToManyField(User, through='StudyMembership')
    domain = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    published = models.BooleanField(_('published'), default=False)
    advanced_filtering = models.BooleanField(
        _('uses advanced filtering for recruitment'), help_text=_(
            'By default you can create only one filtergroup in which all the filters are joined by '
            'AND operator. Advanced filtering allows you to create multiple filtergroups which are '
            'joined by OR operator.'
        ),
        default=False)
    custom_filter = models.CharField(_('custom filter'), max_length=254, blank=True)

    consent = RestrictedFileField(
        _('consent'),
        blank=True,
        upload_to='studies/consent/',
        content_types=['application/pdf'],
        max_upload_size=5000000,
    )

    def __str__(self):
        return self.name

    def clean(self):
        if self.study_type == self.FMRI and not self.data_sensitivity:
            self.data_sensitivity = True
            raise ValidationError(
                _('Data collected by this type of study is always considered sensitive!'),
                code='invalid')
        if self.subjectfiltergroup_set.count() > 1 and not self.advanced_filtering:
            raise ValidationError(_(
                'Studies with more than one filtergroup can\'t be transformed back to basic '
                'filtering. Delete all but one filtergroup first!'), code='invalid')

    def get_filter_max_privacy_level(self):
        key = 'subjectfilter__description__privacy_level_read'
        result = self.subjectfiltergroup_set.aggregate(models.Max(key))
        return result[key + '__max'] or 0

    def raise_permission_denied_if_study_is_published(self, msg=_("study is published")):
        if self.published:
            raise PermissionDenied(msg)

    def raise_404_error_if_study_is_not_published(self):
        if not self.published:
            raise Http404

    @classmethod
    def get_by_pk_or_404(cls, pk):
        return get_object_or_404(cls, pk=pk)

    @property
    def appointment_today(self):
        today = datetime.date.today()
        return self.participationrequest_set.filter(appointment__date=today).exists()

    def has_exclusion_criteria(self):
        return self.exclusion_criteria or self.study_type == self.FMRI


class StudyMembership(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, blank=True, related_name='+')

    class Meta:
        unique_together = ('study', 'user')

    def __str__(self):
        return '{}:{}'.format(self.study, self.user)


class StudySession(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    duration = models.PositiveIntegerField(_('Duration of a session in minutes'))
