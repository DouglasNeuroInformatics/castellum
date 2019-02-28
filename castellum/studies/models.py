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

import uuid

from django.contrib.auth.models import Group
from django.db import models
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from enum import Enum

from castellum.castellum_auth.models import User
from castellum.utils.fields import DateField


class Study(models.Model):

    class StudyTypeEnum(Enum):
        ONLINE = 0
        BEHAVIORAL_LAB = 1
        FMRI = 2
        SIMULATION = 3
        EEG = 4
        THIRD_PARTY = 5

    STUDY_TYPES = [
        (StudyTypeEnum(0), _('Online')),
        (StudyTypeEnum(1), _('Behavioral lab')),
        (StudyTypeEnum(2), 'FMRI'),
        (StudyTypeEnum(3), _('Simulation')),
        (StudyTypeEnum(4), _('EEG')),
        (StudyTypeEnum(5), _('3rd Party')),
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
    sessions_count = models.PositiveIntegerField(
        _('number of test sessions per subject'), blank=True, null=True)
    session_duration = models.PositiveIntegerField(
        _('Duration of a session in minutes'), blank=True, null=True)
    sessions_start = DateField(_('start of test sessions'), blank=True, null=True)
    sessions_end = DateField(_('end of test sessions'), blank=True, null=True)

    members = models.ManyToManyField(User, through='StudyMembership')
    domain = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    published = models.BooleanField(_('published'), default=False)

    def __str__(self):
        return self.name

    def clean(self):
        if self.study_type == repr(self.StudyTypeEnum.FMRI) and not self.data_sensitivity:
            self.data_sensitivity = True
            raise ValidationError(
                _('Data collected by this type of study is always considered sensitive!'))


class StudyMembership(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, blank=True, related_name='+')

    class Meta:
        unique_together = ('study', 'user')

    def __str__(self):
        return '{}:{}'.format(self.study, self.user)
