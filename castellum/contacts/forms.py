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

from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from castellum.utils.forms import DatalistWidget

from .models import Address
from .models import City
from .models import Contact
from .models import Country


class AddressForm(forms.ModelForm):

    country = forms.CharField(max_length=64, widget=DatalistWidget(
        datalist=Country.objects.values_list('name', flat=True)))
    city = forms.CharField(max_length=128, widget=DatalistWidget(
        datalist=City.objects.values_list('name', flat=True)))

    class Meta:
        model = Address
        exclude = ('city',)


class ContactForm(forms.ModelForm):
    ADDRESS_FIELDS = [
        'country', 'city', 'zip_code', 'street', 'house_number', 'additional_information',
    ]

    # fields required for the address
    country = forms.CharField(label=_('Country'), required=False, widget=DatalistWidget(
        datalist=Country.objects.values_list('name', flat=True)))
    city = forms.CharField(label=_('City'), required=False, widget=DatalistWidget(
        datalist=City.objects.values_list('name', flat=True)))
    zip_code = forms.CharField(label=_('Zip code'), required=False)
    street = forms.CharField(label=_('Street'), required=False)
    house_number = forms.CharField(label=_('House number'), required=False)
    additional_information = forms.CharField(
        label=_('Additional address information'), required=False)

    has_guardian = forms.ChoiceField(required=False, choices=[
        ('self', _('Full of age')),
        ('guardians', _('Has legal guardian')),
    ], widget=forms.RadioSelect)

    class Meta:
        model = Contact
        exclude = ('address',)
        widgets = {
            'guardians': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.address:
            self.fields['country'].initial = self.instance.address.city.country.name
            self.fields['city'].initial = self.instance.address.city.name
            self.fields['zip_code'].initial = self.instance.address.zip_code
            self.fields['street'].initial = self.instance.address.street
            self.fields['house_number'].initial = self.instance.address.house_number
            self.fields['additional_information'].initial = \
                self.instance.address.additional_information

        if self.instance.has_guardian:
            self.fields['has_guardian'].initial = 'guardians'
        elif self.instance.is_complete:
            self.fields['has_guardian'].initial = 'self'

        self.fields['date_of_birth'].required = True

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('has_guardian') == 'guardians':
            for name in self.ADDRESS_FIELDS:
                cleaned_data[name] = ''
            cleaned_data['phone_number'] = ''
            cleaned_data['phone_number_alternative'] = ''
            cleaned_data['email'] = ''
            cleaned_data['preferred_contact_method'] = ''
        else:
            cleaned_data['guardians'] = []

        date_of_birth = cleaned_data.get('date_of_birth')
        phone_number = cleaned_data.get('phone_number', '')
        email = cleaned_data.get('email', '')
        preferred_contact_method = cleaned_data.get('preferred_contact_method', '')
        guardians = cleaned_data.get('guardians')
        has_guardian = guardians and guardians.exists()

        age = datetime.date.today() - date_of_birth
        if not has_guardian and age.days // 365 < 18:
            msg = _('Subjects under the age of 18 need a legal guardian.')
            raise ValidationError(msg, code='invalid')

        has_address = any(cleaned_data.get(name) for name in self.ADDRESS_FIELDS)
        if has_address:
            address_form = AddressForm(data=cleaned_data)
            if not address_form.is_valid():
                if address_form.errors:
                    for field, errors in address_form.errors.items():
                        self.add_error(field, errors)

                raise ValidationError(_("Provide more details for the address."), code='invalid')
        else:
            if not any([phone_number, email, has_guardian]):
                msg = _("Either email, phone number, address, or guardian should be provided.")
                raise ValidationError(msg, code='invalid')

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

    def save(self, commit=True):
        contact = super().save(commit=False)

        if self.cleaned_data.get('city'):
            country, __ = Country.objects.get_or_create(name=self.cleaned_data['country'])
            city, __ = City.objects.get_or_create(name=self.cleaned_data['city'], country=country)

            if not contact.address:
                contact.address = Address.objects.create(city=city)
            else:
                contact.address.city = city

            contact.address.zip_code = self.cleaned_data['zip_code']
            contact.address.street = self.cleaned_data['street']
            contact.address.house_number = self.cleaned_data['house_number']
            contact.address.additional_information = self.cleaned_data['additional_information']

            if commit:
                contact.address.save()

        if commit:
            contact.save()
            self.save_m2m()

            if not self.cleaned_data.get('city') and contact.address:
                contact.address.delete()

        return contact


class SearchForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'first_name',
            'last_name',
        ]
