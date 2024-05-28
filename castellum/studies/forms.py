# (c) 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>,
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

from django import forms
from django.conf import settings
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from castellum.castellum_auth.models import User
from castellum.utils import scheduler
from castellum.utils.forms import TagField

from .models import Study
from .models import StudyMembership
from .models import StudySession
from .models import StudyTag
from .models import StudyType


class StudyForm(forms.ModelForm):
    tags = TagField(label=_('Tags'), required=False)

    class Meta:
        model = Study
        fields = [
            'name',
            'contact_person',
            'phone',
            'email',
            'min_subject_count',
            'exportable_attributes',
            *settings.CASTELLUM_ENABLE_STUDY_METADATA,
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['tags'].initial = list(self.instance.tags)

        self.fields['tags'].choices = self.get_tag_choices()

    def get_tag_choices(self):
        tags = set(StudyTag.objects.values_list('name', flat=True).distinct())
        if self.data:
            widget = self.fields['tags'].widget
            tags.update(widget.value_from_datadict(self.data, {}, 'tags'))
        return [(name, name) for name in sorted(tags)]

    def save(self, *args, **kwargs):
        obj = super().save(*args, **kwargs)

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
    start = forms.DateTimeField()
    end = forms.DateTimeField()


class SessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = [
            'name',
            'duration',
            'resources',
            'type',
            'first_reminder_days',
            'second_reminder_days',
            'reminder_text',
            'schedule_id',
        ]
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
            raise forms.ValidationError(_(
                'Schedule ID can no longer be changed once appointments have '
                'been scheduled'
            ))

        if settings.SCHEDULER_URL and value:
            try:
                scheduler.get_bulk(value)
            except Exception as e:
                raise forms.ValidationError(
                    _('A schedule with this ID does not exist')
                ) from e

        return value


class StudyRecruitmentSettingsForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = [
            'advanced_filtering',
            'recruitment_text',
            'is_exclusive',
            'complete_matches_only',
            'recruitment_active_after',
            'recruitment_active_before',
            'geo_filter',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'castellum.geofilters' not in settings.INSTALLED_APPS:
            self.fields.pop('geo_filter')

    def clean(self):
        cleaned_data = super().clean()
        after = cleaned_data['recruitment_active_after']
        before = cleaned_data['recruitment_active_before']

        if after:
            today = datetime.date.today()
            if today < after + settings.CASTELLUM_MINIMUM_ACTIVITY_PERIOD:
                self.add_error('recruitment_active_after', format_lazy(
                    _('Must be at least {} days ago'),
                    settings.CASTELLUM_MINIMUM_ACTIVITY_PERIOD.days,
                ))
            elif before and before < after + settings.CASTELLUM_MINIMUM_ACTIVITY_PERIOD:
                self.add_error('recruitment_active_after', format_lazy(
                    _('Before and after must be at least {} days apart'),
                    settings.CASTELLUM_MINIMUM_ACTIVITY_PERIOD.days,
                ))

        return cleaned_data


class OtherStudiesForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['excluded_studies', 'included_studies']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Study.objects.exclude(pk=self.instance.pk)
        self.fields['excluded_studies'].queryset = qs
        self.fields['excluded_studies'].widget.attrs['class'] = 'form-control'
        self.fields['included_studies'].queryset = qs
        self.fields['included_studies'].widget.attrs['class'] = 'form-control'


class MemberForm(forms.ModelForm):
    class Meta:
        model = StudyMembership
        fields = ['groups']
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }


class MultiMemberForm(MemberForm):
    users = forms.ModelMultipleChoiceField(User.objects.all(), label=_('Users'))

    def save(self):
        for user in self.cleaned_data['users']:
            self.instance.pk = None
            self.instance.user = user
            self.instance.save()
            self._save_m2m()


class MailSettingsForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = [
            'mail_subject',
            'mail_body',
        ]

    def clean_mail_body(self):
        value = self.cleaned_data['mail_body']
        if not value:
            return value
        if '{name}' not in value:
            raise forms.ValidationError(_(
                'Without a "{name}" placeholder, recipients cannot '
                'know who exactly this mail is intended to reach.'
            ))
        return value
