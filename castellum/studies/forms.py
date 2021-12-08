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

import json
from pathlib import Path

from django import forms
from django.conf import settings
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from castellum.castellum_auth.models import User
from castellum.utils import scheduler
from castellum.utils.forms import BaseImportForm
from castellum.utils.forms import TagField

from .models import Study
from .models import StudyMembership
from .models import StudySession
from .models import StudyTag
from .models import StudyType

APP_DIR = Path(__file__).resolve().parent
IMPORT_SCHEMA = json.load(open(APP_DIR / 'schemas' / 'study.json'))


class StudyForm(forms.ModelForm):
    tags = TagField(label=_('Tags'), required=False)

    class Meta:
        model = Study
        fields = [
            'name',
            'contact_person',
            'principal_investigator',
            'affiliated_scientists',
            'affiliated_research_assistants',
            'phone',
            'email',
            'description',
            'announce_status_changes',
            'consent',
            'min_subject_count',
            'exportable_attributes',
            'is_onetime_invitation',
        ]
        help_texts = {
            'announce_status_changes': format_lazy(
                _('Mails will be sent to: {}'),
                ', '.join(settings.CASTELLUM_STUDY_STATUS_NOTIFICATION_TO)
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            del self.fields['is_onetime_invitation']

        if self.instance.pk:
            self.fields['tags'].initial = list(self.instance.tags)

        self.fields['tags'].choices = self.get_tag_choices()

    def get_tag_choices(self):
        tags = set(StudyTag.objects.values_list('name', flat=True).distinct())
        if self.data:
            widget = self.fields['tags'].widget
            tags.update(widget.value_from_datadict(self.data, {}, 'tags'))
        return [(name, name) for name in sorted(tags)]

    def save(self, commit=True):
        obj = super().save(commit=commit)

        for tag in obj.studytag_set.all():
            if tag.name not in self.cleaned_data['tags']:
                tag.delete()
        for name in self.cleaned_data['tags']:
            obj.studytag_set.get_or_create(name=name)

        return obj


class StudyFilterForm(forms.Form):
    q = forms.CharField(label=_('Search'))
    display = forms.ChoiceField(choices=[
        ('list', _('List')),
        ('calendar', _('Calendar')),
    ])
    member = forms.ChoiceField(label=_('Membership'), choices=[
        ('my', _('Mine')),
        ('all', _('All')),
    ])
    status = forms.ChoiceField(label=_('Status'), choices=Study.STATUS)
    type = forms.ModelChoiceField(
        label=_('Type'), queryset=StudyType.objects, empty_label=None
    )
    is_onetime_invitation = forms.BooleanField(label=_('One time invitation'))
    start = forms.DateTimeField()
    end = forms.DateTimeField()

    def clean(self):
        cleaned_data = super().clean()
        if self.data.get('type') == 'onetime_invitation':
            cleaned_data['is_onetime_invitation'] = True
        return cleaned_data


class SessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = ['name', 'duration', 'resource', 'type', 'reminder_text', 'schedule_id']
        help_texts = {
            'reminder_text': format_lazy(_(
                'All subjects will be reminded {} days before each appointment.'
            ), settings.CASTELLUM_APPOINTMENT_REMINDER_PERIOD.days)
        }
        widgets = {
            'type': forms.CheckboxSelectMultiple(),
        }

    def clean_schedule_id(self):
        value = self.cleaned_data['schedule_id']

        if (
            self.instance.pk
            and self.instance.schedule_id != value
            and self.instance.appointment_set.exists()
        ):
            raise forms.ValidationError(
                _('Schedule ID can no longer be changed once appointments have been scheduled')
            )

        if settings.SCHEDULER_URL and value:
            try:
                scheduler.get_bulk(value)
            except Exception as e:
                raise forms.ValidationError(_('A schedule with this ID does not exist')) from e

        return value


class ExcludedStudiesForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['excluded_studies']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['excluded_studies'].queryset = Study.objects.exclude(pk=self.instance.pk)
        self.fields["excluded_studies"].widget.attrs['class'] = 'form-control'


class AddMemberForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())


class MemberForm(forms.ModelForm):
    class Meta:
        model = StudyMembership
        fields = ['groups']
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }


class ImportForm(BaseImportForm):
    schema = IMPORT_SCHEMA
    schema_ref = '#/$defs/Study'
