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

from django import forms
from django.conf import settings
from django.forms import ValidationError
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from castellum.subjects.models import Subject
from castellum.utils.forms import DatalistWidget

from .models import Address
from .models import Contact


class SubjectMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        # Getting subject.contact is expensive (separate database).
        # Since we only render the selected choices it makes sense to calculate it lazily.
        return lazy(lambda: obj.contact.full_name, str)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['contact']
        widgets = {
            'country': DatalistWidget(datalist=(
                Address.objects.order_by('country').values_list('country', flat=True).distinct
            )),
            'city': DatalistWidget(datalist=(
                Address.objects.order_by('city').values_list('city', flat=True).distinct
            )),
        }


class ContactForm(forms.ModelForm):
    guardians_pane = forms.ChoiceField(required=False, choices=[
        ('self', _('Full of age')),
        ('guardians', _('Has legal guardian')),
    ], widget=forms.RadioSelect)
    guardians_remove = forms.ModelMultipleChoiceField(Subject.objects, required=False)
    guardians_add = SubjectMultipleChoiceField(Subject.objects, required=False)

    class Meta:
        model = Contact
        exclude = ['guardians']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        is_guardian = kwargs.pop('is_guardian', False)
        super().__init__(*args, **kwargs)

        if self.instance.is_guardian:
            is_guardian = True

        self.address = self.get_address_form(**kwargs)

        if self.instance.has_guardian:
            self.fields['guardians_pane'].initial = 'guardians'
        elif any([self.instance.get_address(), self.instance.phone_number, self.instance.email]):
            self.fields['guardians_pane'].initial = 'self'

        self.fields['guardians_remove'].choices = self.get_guardians_rm_choices(user)

        self.fields['date_of_birth'].required = not is_guardian

    def get_address_form(self, **kwargs):
        address_kwargs = kwargs.copy()
        if kwargs.get('instance'):
            address_kwargs['instance'] = kwargs['instance'].get_address()
        form = AddressForm(**address_kwargs)
        for field in form.fields.values():
            field.required = False
        return form

    def get_guardians_rm_choices(self, user):
        self.guardians_blocked = 0
        if self.instance.id:
            for contact in self.instance.guardians.all():
                if user.has_privacy_level(contact.subject.privacy_level):
                    yield (contact.subject.pk, contact.full_name)
                else:
                    self.guardians_blocked += 1

    def clean(self):
        cleaned_data = super().clean()

        is_guardians_pane = cleaned_data.get('guardians_pane') == 'guardians'
        date_of_birth = cleaned_data.get('date_of_birth')
        phone_number = cleaned_data.get('phone_number', '')
        email = cleaned_data.get('email', '')
        preferred_contact_method = cleaned_data.get('preferred_contact_method', '')

        # clear unselected pane
        if is_guardians_pane:
            cleaned_data['phone_number'] = ''
            cleaned_data['phone_number_alternative'] = ''
            cleaned_data['email'] = ''
            cleaned_data['preferred_contact_method'] = ''

        has_address = any(self.data.get(name) for name in self.address.fields)

        # validate guardian required for underage subjects
        if date_of_birth:
            age = datetime.date.today() - date_of_birth
            if not is_guardians_pane and age.days // 365 < settings.CASTELLUM_FULL_AGE:
                msg = _(
                    'Subjects under the age of %i need a legal guardian.'
                ) % settings.CASTELLUM_FULL_AGE
                raise ValidationError(msg, code='invalid')

        # validate address
        if has_address:
            # populate self.address.cleaned_data
            self.address.is_valid()

            # do strict validation (with required)
            address_form = AddressForm(data=self.data)
            if not address_form.is_valid():
                if address_form.errors:
                    for field, errors in address_form.errors.items():
                        self.address.add_error(field, errors)

                raise ValidationError(_("Provide more details for the address."), code='invalid')

        # validate preferred_contact_method is set
        if not has_address and preferred_contact_method == 'postal':
            self.add_error('preferred_contact_method', _("Chosen contact method can not be saved."))
            self.add_error(None, _("Please provide a complete address."))
        if not phone_number and preferred_contact_method == 'phone':
            self.add_error('preferred_contact_method', _("Chosen contact method can not be saved."))
            self.add_error(None, _("Please provide a phone number."))
        if not email and preferred_contact_method == 'email':
            self.add_error('preferred_contact_method', _("Chosen contact method can not be saved."))
            self.add_error(None, _("Please provide an email."))

        return cleaned_data

    def save(self):
        contact = super().save()

        has_address = any(self.data.get(name) for name in self.address.fields)
        if has_address and self.cleaned_data.get('guardians_pane') != 'guardians':
            self.address.instance.contact = contact
            self.address.save()
        elif contact.get_address():
            contact.address.delete()
            # refresh from db
            contact = Contact.objects.get(pk=contact.pk)

        if self.cleaned_data.get('guardians_pane') == 'guardians':
            contact.guardians.remove(*[
                subject.contact for subject in self.cleaned_data.get('guardians_remove', [])
            ])

            contact.guardians.add(*[
                subject.contact for subject in self.cleaned_data.get('guardians_add', [])
            ])
        else:
            contact.guardians.set([])

        return contact


class SearchForm(forms.Form):
    search = forms.CharField(label=_('Search for name or email address'), required=True)

    def clean(self):
        cleaned_data = super().clean()

        search = cleaned_data.get('search', '')

        names = [part for part in search.split() if '@' not in part]
        emails = [part for part in search.split() if '@' in part]

        cleaned_data['first_name'] = names[0] if names else ''
        cleaned_data['last_name'] = ' '.join(names[1:])
        cleaned_data['email'] = emails[0] if emails else ''

        return cleaned_data
