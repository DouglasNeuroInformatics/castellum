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

from huscy.projects.models import Project
from huscy.projects.models import ResearchUnit

from castellum.castellum_auth.models import User
from castellum.utils.forms import BaseImportForm
from castellum.utils.forms import ReadonlyModelForm

from . import models

APP_DIR = os.path.dirname(__file__)
IMPORT_SCHEMA = json.load(open(os.path.join(APP_DIR, 'schemas', 'study.json')))


class StudyForm(ReadonlyModelForm):
    title = Project._meta.get_field('title').formfield(label=_('Name'))
    description = Project._meta.get_field('description').formfield(label=_('Description'))

    class Meta:
        model = models.Study
        fields = [
            'contact_person',
            'principal_investigator',
            'affiliated_scientists',
            'affiliated_research_assistants',
            'keywords',
            'study_type',
            'data_sensitivity',
            'consent',
            'min_subject_count',
            'expense_allowance',
            'sessions_start',
            'sessions_end',
        ]
        widgets = {
            'study_type': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.project_id:
            self.initial['title'] = self.instance.project.title
            self.initial['description'] = self.instance.project.description

    def save(self):
        if self.instance.project_id:
            self.instance.project.title = self.cleaned_data['title']
            self.instance.project.description = self.cleaned_data['description']
            self.instance.project.save()
        else:
            dummy_user, __ = User.objects.get_or_create(username='dummy')
            dummy_unit, __ = ResearchUnit.objects.get_or_create(
                name='dummy', code='dummy', principal_investigator=dummy_user
            )
            self.instance.project = Project.objects.create(
                title=self.cleaned_data['title'],
                description=self.cleaned_data['description'],
                research_unit=dummy_unit,
                principal_investigator=dummy_user,
                local_id=Project.objects.get_next_local_id(dummy_unit),
            )
        return super().save()


class ExcludedStudiesForm(ReadonlyModelForm):
    class Meta:
        model = models.Study
        fields = ('excluded_studies',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['excluded_studies'].queryset = models.Study.objects.exclude(pk=self.instance.pk)
        self.fields["excluded_studies"].widget.attrs['class'] = 'form-control'


class AddMemberForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())


class MemberForm(forms.ModelForm):
    class Meta:
        model = models.StudyMembership
        fields = ('groups',)
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }


class ImportForm(BaseImportForm):
    schema = IMPORT_SCHEMA
    schema_ref = '#/$defs/Study'
