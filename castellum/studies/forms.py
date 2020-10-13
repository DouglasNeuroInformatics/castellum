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

import json
import os

from django import forms
from django.utils.translation import gettext_lazy as _

from castellum.castellum_auth.models import User
from castellum.utils.forms import BaseImportForm
from castellum.utils.forms import ReadonlyModelForm

from . import models

APP_DIR = os.path.dirname(__file__)
IMPORT_SCHEMA = json.load(open(os.path.join(APP_DIR, 'schemas', 'study.json')))


class StudyForm(ReadonlyModelForm):
    class Meta:
        model = models.Study
        fields = [
            'name',
            'contact_person',
            'principal_investigator',
            'affiliated_scientists',
            'affiliated_research_assistants',
            'phone',
            'email',
            'description',
            'keywords',
            'is_relevant_for_pr',
            'data_sensitivity',
            'consent',
            'min_subject_count',
        ]


class StudyFilterForm(forms.Form):
    q = forms.CharField(label=_('Search'), help_text=_('Search for title or contact person'))
    display = forms.ChoiceField(choices=[
        ('list', _('List')),
        ('calendar', _('Calendar')),
    ])
    member = forms.ChoiceField(label=_('Membership'), choices=[
        ('my', _('Mine')),
        ('all', _('All')),
    ])
    status = forms.ChoiceField(label=_('Status'), choices=models.Study.STATUS)
    type = forms.ModelChoiceField(
        label=_('Type'), queryset=models.StudyType.objects, empty_label=None
    )
    is_onetime_invitation = forms.BooleanField(label=_('One time invitation'))
    start = forms.DateTimeField()
    end = forms.DateTimeField()


class SessionForm(ReadonlyModelForm):
    class Meta:
        model = models.StudySession
        fields = ['name', 'duration', 'resource', 'type']
        widgets = {
            'type': forms.CheckboxSelectMultiple(),
        }


class ExcludedStudiesForm(ReadonlyModelForm):
    class Meta:
        model = models.Study
        fields = ['excluded_studies']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['excluded_studies'].queryset = models.Study.objects.exclude(pk=self.instance.pk)
        self.fields["excluded_studies"].widget.attrs['class'] = 'form-control'


class AddMemberForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())


class MemberForm(forms.ModelForm):
    class Meta:
        model = models.StudyMembership
        fields = ['groups']
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }


class ImportForm(BaseImportForm):
    schema = IMPORT_SCHEMA
    schema_ref = '#/$defs/Study'
