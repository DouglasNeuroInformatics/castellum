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

from django import forms
from django.forms import ValidationError
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from .models import Address
from .models import City
from .models import Country
from .models import Subject


class DatalistWidget(TextInput):
    template_name = 'subject_management/widgets/datalist.html'

    def __init__(self, *args, datalist=[], **kwargs):
        self.datalist = datalist
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['list'] = context['widget']['attrs']['id'] + '_list'
        context['datalist'] = self.datalist
        return context


class SubjectForm(forms.ModelForm):

    phone_number = PhoneNumberField(label=_("Phone number"), required=False)
    phone_number_alternative = PhoneNumberField(label=_("Alternative phone number"), required=False)

    # fields required for the address
    country = forms.CharField(widget=DatalistWidget(
        datalist=Country.objects.values_list('name', flat=True)), required=False)
    city = forms.CharField(widget=DatalistWidget(
        datalist=City.objects.values_list('name', flat=True)), required=False)
    zip_code = forms.CharField(required=False)
    street = forms.CharField(required=False)
    house_number = forms.CharField(required=False)
    additional_information = forms.CharField(required=False)

    class Meta:
        model = Subject
        exclude = ('address',)

        widgets = {
            'phone_number': PhoneNumberInternationalFallbackWidget(
                attrs={'placeholder': _('Phone (ex. +4917693333333)')}),
            'phone_number_alternative': PhoneNumberInternationalFallbackWidget(
                attrs={'placeholder': _('Alternative phone (ex. +4917693333333)')}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.address:
            self.fields['country'].initial = self.instance.address.city.country
            self.fields['city'].initial = self.instance.address.city
            self.fields['zip_code'].initial = self.instance.address.zip_code
            self.fields['street'].initial = self.instance.address.street
            self.fields['house_number'].initial = self.instance.address.house_number
            self.fields['additional_information'].initial = \
                self.instance.address.additional_information

    def clean(self):
        cleaned_data = super().clean()

        country_str = cleaned_data.get('country', '')
        city_str = cleaned_data.get('city', '')
        zip_code_str = cleaned_data.get('zip_code', '')
        street_str = cleaned_data.get('street', '')
        house_number_str = cleaned_data.get('house_number', '')
        phone_number_str = cleaned_data.get('phone_number', '')
        email_str = cleaned_data.get('email', '')

        full_address = False
        if all([country_str, city_str, zip_code_str, street_str, house_number_str]):
            full_address = True

        incomplete_address = False
        if not full_address:
            if any([country_str, city_str, zip_code_str, street_str, house_number_str]):
                incomplete_address = True

        # check if address has all the required fields
        if not any([phone_number_str, email_str]):
            if incomplete_address:
                raise ValidationError(_("Provide more details for the address"))

        # check if there is at least address, phone_number or email.
        if not any([full_address, phone_number_str, email_str]):
            raise ValidationError(_("Either email, phone number or address should be provided"))

        # check if there is such country in the database
        if country_str:
            country = Country.objects.filter(name=country_str).first()
            if country:
                # check if there is such city in the country
                if city_str:
                    city = City.objects.filter(name=city_str, country=country).first()
                    if not city:
                        msg = 'We can not find city for given country in our database.'
                        self._errors['city'] = self.error_class([msg])
                        return cleaned_data
            else:
                msg = 'There is no such country in our database.'
                self._errors['country'] = self.error_class([msg])
                return cleaned_data

        return cleaned_data

    def save(self, commit=True):
        subject = super().save(commit=False)

        city = City.objects.get(name=self.cleaned_data['city'])

        if not subject.address:
            subject.address = Address.objects.create(city=city)
        else:
            subject.address.city = city

        subject.address.zip_code = self.cleaned_data['zip_code']
        subject.address.street = self.cleaned_data['street']
        subject.address.house_number = self.cleaned_data['house_number']
        subject.address.additional_information = self.cleaned_data['additional_information']

        if commit:
            subject.address.save()
            subject.save()

        return subject
