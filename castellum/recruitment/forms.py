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

import itertools
import json
import os

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _

from castellum.studies.models import Study
from castellum.utils.forms import BaseImportForm
from castellum.utils.forms import DateTimeField
from castellum.utils.forms import DisabledChoiceField
from castellum.utils.forms import DisabledModelChoiceField

from .models import Appointment
from .models import AttributeDescription
from .models import AttributeSet
from .models import Participation
from .models import SubjectFilter
from .models.appointments import MINUTE
from .models.attributesets import ANSWER_DECLINED
from .models.attributesets import UNCATEGORIZED

APP_DIR = os.path.dirname(__file__)
IMPORT_SCHEMA = json.load(open(os.path.join(APP_DIR, 'schemas', 'attributes.json')))


def get_description_choices(user):
    choices = [(None, '---')]
    disabled_choices = []

    categories = AttributeDescription.objects.by_category()

    for description in categories.pop(UNCATEGORIZED):
        choices.append((description.pk, description.filter_label))
        if not user.has_privacy_level(description.privacy_level_read):
            disabled_choices.append(description.pk)

    for category, descriptions in categories.items():
        sub = []
        for description in descriptions:
            sub.append((description.pk, description.filter_label))
            if not user.has_privacy_level(description.privacy_level_read):
                disabled_choices.append(description.pk)
        choices.append((category.label, sub))

    return choices, disabled_choices


class SubjectFilterAddForm(forms.Form):
    description = DisabledModelChoiceField(AttributeDescription.objects.none(), required=False)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices, disabled_choices = get_description_choices(user)
        self.fields["description"].choices = choices
        self.fields["description"].widget.disabled_choices = disabled_choices


class SubjectFilterForm(forms.ModelForm):
    class Meta:
        model = SubjectFilter
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        selected_description = self._get_selected_description(**kwargs)

        self.fields["value"] = selected_description.field.filter_formfield(required=True)
        self.fields["operator"] = forms.ChoiceField(
            choices=selected_description.field.available_operators
        )

        try:
            if self.instance.group.study.status != Study.EDIT:
                self.fields["value"].widget.attrs["disabled"] = True
                self.fields["operator"].widget.attrs["disabled"] = True
        except ObjectDoesNotExist:
            pass

    def _get_selected_description(self, instance=None, data=None, prefix=None, **kwargs):
        if instance:
            return instance.description

        key = prefix + '-description' if prefix else 'description'
        if data and data[key]:
            try:
                return AttributeDescription.objects.get(pk=data[key])
            except AttributeDescription.DoesNotExist:
                return None

        try:
            return kwargs['initial']['description']
        except KeyError:
            return None


class SubjectFilterFormSet(forms.BaseModelFormSet):
    def clean(self):
        super().clean()

        values = []
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                values.append((
                    form.cleaned_data.get('description'),
                    form.cleaned_data.get('operator'),
                    form.cleaned_data.get('value'),
                ))

        if len(set(values)) != len(values):
            raise forms.ValidationError(_(
                'There are duplicates in filters. Please change or delete filters!'
            ), code='invalid')


class AttributeSetForm(forms.ModelForm):

    class Meta:
        model = AttributeSet
        exclude = ['data']
        widgets = {
            'study_type_disinterest': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, instance=None, **kwargs):
        if not kwargs.get('initial'):
            kwargs['initial'] = {}
            for key, value in instance.get_data().items():
                kwargs['initial'][key] = None if value == ANSWER_DECLINED else value
        super().__init__(instance=instance, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        for key in cleaned_data:
            if key + '_answer_declined' in self.data:
                cleaned_data[key] = ANSWER_DECLINED
        study_type_disinterest = cleaned_data.pop('study_type_disinterest')
        onetime_invitation_disinterest = cleaned_data.pop('onetime_invitation_disinterest')
        return {
            'study_type_disinterest': study_type_disinterest,
            'onetime_invitation_disinterest': onetime_invitation_disinterest,
            'data': cleaned_data,
        }

    def save(self):
        self.instance.data.update(self.cleaned_data['data'])
        return super().save()

    @classmethod
    def factory(cls, user, obj=None):
        allowed_descriptions = AttributeDescription.objects.allowed_write(user, obj=obj)
        form_fields = {desc.json_key: desc.field.formfield() for desc in allowed_descriptions}
        return type('AttributeSetForm', (cls,), form_fields)


class AppointmentsForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for session, appointment in self.instance.get_appointments():
            key = 'appointment-%i' % session.pk
            self.fields[key] = DateTimeField(
                label=self.format_session_name(session),
                initial=appointment.start if appointment else None,
                required=False,
            )

    def format_session_name(self, session):
        duration = _('%imin') % session.duration
        types = ', '.join(str(t) for t in session.type.order_by('pk'))
        if types:
            return '%s (%s) - %s' % (session.name, types, duration)
        else:
            return '%s - %s' % (session.name, duration)

    def clean(self):
        cleaned_data = super().clean()

        appointments = []
        for session in self.instance.study.studysession_set.all():
            key = 'appointment-%i' % session.pk
            start = cleaned_data.get(key)
            if start:
                appointments.append((session, key, start, start + session.duration * MINUTE))

        for a, b in itertools.combinations(appointments, 2):
            __, key1, start1, end1 = a
            __, key2, start2, end2 = b
            if start1 < end2 and start2 < end1:
                self.add_error(key1, _('Appointments must not overlap.'))
                self.add_error(key2, _('Appointments must not overlap.'))
                break

        qs = Appointment.objects\
            .exclude(participation=self.instance)\
            .filter(participation__status=Participation.INVITED)\
            .annotate(end=models.ExpressionWrapper(
                models.F('start') + models.F('session__duration') * MINUTE,
                output_field=models.DateTimeField(),
            ))

        for session, key, start, end in appointments:
            if session.resource and qs.filter(
                session__resource=session.resource, end__gt=start, start__lt=end,
            ).exists():
                self.add_error(key, _('The required resource is not available at this time'))

    def save(self):
        pariticipation = super().save()
        self.appointment_changes = []

        for session, appointment in pariticipation.get_appointments():
            start = self.cleaned_data.get('appointment-%i' % session.pk)

            if appointment:
                if not start:
                    self.appointment_changes.append((appointment.start, None))
                    appointment.delete()
                elif start != appointment.start:
                    self.appointment_changes.append((appointment.start, start))
                    appointment.start = start
                    appointment.reminded = False
                    appointment.show_up = Appointment.SHOWUP  # reset to default
                    appointment.save()
            elif start:
                self.appointment_changes.append((None, start))
                pariticipation.appointment_set.create(
                    session=session,
                    start=start,
                )

        return pariticipation

    @property
    def appointments(self):
        for name in self.fields:
            if name.startswith('appointment-'):
                yield self[name]


class ContactForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = ['status', 'followup_date', 'followup_time', 'exclusion_criteria_checked']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        model_status = Participation._meta.get_field('status')
        self.fields['status'] = DisabledChoiceField(
            label=model_status.verbose_name,
            choices=model_status.choices,
            coerce=int,
        )
        if not self.instance.match:
            self.fields['status'].widget.disabled_choices = [
                choice for choice, label in Participation.STATUS_OPTIONS
                if choice != Participation.UNSUITABLE
            ]
        elif self.instance.match == 'incomplete':
            self.fields['status'].widget.disabled_choices = [Participation.INVITED]


class ContactAndAppointmentsForm(ContactForm, AppointmentsForm):
    pass


class SendMailForm(forms.Form):
    batch_size = forms.IntegerField(
        min_value=1, label=_('How many subjects do you want to contact?')
    )


class DescriptionImportForm(BaseImportForm):
    schema = IMPORT_SCHEMA
    schema_ref = '#/$defs/AttributeDescriptionExport'
