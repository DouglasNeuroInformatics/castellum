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
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from castellum.studies.models import Study
from castellum.utils.forms import BaseImportForm
from castellum.utils.forms import DateTimeField
from castellum.utils.forms import DisabledChoiceField
from castellum.utils.forms import DisabledModelChoiceField

from .models import Appointment
from .models import AttributeDescription
from .models import AttributeSet
from .models import ParticipationRequest
from .models import SubjectFilter
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
        exclude = ('data',)
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
        return {
            'study_type_disinterest': study_type_disinterest,
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


class AppointmentForm(forms.ModelForm):
    """A form with one DateTimeField for each session."""

    class Meta:
        model = ParticipationRequest
        fields = ()

    @classmethod
    def factory(cls, instance):
        props = {'field_order': []}
        sessions = instance.study.studysession_set.all()
        for session in sessions:
            key = 'session-%i' % session.pk
            props['field_order'].append(key)
            props[key] = DateTimeField(label=session.name, required=False)
        return type('AppointmentForm', (cls,), props)

    def __init__(self, instance=None, **kwargs):
        if not kwargs.get('initial') and instance:
            kwargs['initial'] = {}
            for appointment in instance.appointment_set.all():
                key = 'session-%i' % appointment.session.pk
                kwargs['initial'][key] = appointment.start
        super().__init__(instance=instance, **kwargs)

    def clean(self):
        """Check for resource collisions.

        If we would just run appointment.clean() for each appointment,
        we would only check for collisions with appointments that are
        already in the database. In order to include the updates from
        this form, we save all changes to the database first. If the
        validation fails, the changes are rolled back.
        """

        transaction.set_autocommit(False)

        cleaned_data = super().clean()
        appointments = []
        sessions = self.instance.study.studysession_set.all()

        for session in sessions:
            key = 'session-%i' % session.pk
            start = cleaned_data.get(key)
            if start:
                try:
                    appointment = Appointment.objects.get(
                        session=session, participant=self.instance
                    )
                    appointment.start = start
                    appointment.save()
                except Appointment.DoesNotExist:
                    appointment = Appointment.objects.create(
                        session=session, participant=self.instance, start=start
                    )
                appointments.append(appointment)
            else:
                Appointment.objects.filter(session=session, participant=self.instance).delete()

        for appointment in appointments:
            key = 'session-%i' % appointment.session.pk
            try:
                appointment.clean()
            except forms.ValidationError as e:
                self.add_error(key, e)

        if self.errors:
            transaction.rollback()
        else:
            transaction.commit()
        transaction.set_autocommit(True)


class ContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        model_status = ParticipationRequest._meta.get_field('status')
        self.fields['status'] = DisabledChoiceField(
            label=model_status.verbose_name,
            choices=model_status.choices,
            coerce=int,
        )
        if not self.instance.match:
            self.fields['status'].widget.disabled_choices = [
                choice for choice, label in ParticipationRequest.STATUS_OPTIONS
                if choice != ParticipationRequest.UNSUITABLE
            ]
        elif self.instance.match == 'incomplete':
            self.fields['status'].widget.disabled_choices = [ParticipationRequest.INVITED]

    class Meta:
        model = ParticipationRequest
        fields = ['status', 'followup_date', 'followup_time', 'exclusion_criteria_checked']


class SendMailForm(forms.Form):
    batch_size = forms.IntegerField(
        min_value=1, label=_('How many subjects do you want to contact?')
    )


class CategoryImportForm(BaseImportForm):
    schema = IMPORT_SCHEMA
    schema_ref = '#/$defs/AttributeCategoryExport'


class DescriptionImportForm(BaseImportForm):
    schema = IMPORT_SCHEMA
    schema_ref = '#/$defs/AttributeDescriptionExport'
