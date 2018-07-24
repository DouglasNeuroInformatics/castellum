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


class AddressForm(forms.Form):

    country = forms.CharField()
    city = forms.CharField()
    zip_code = forms.CharField()
    street = forms.CharField()
    house_number = forms.CharField()
    additional_information = forms.CharField(required=False)

    class Meta:
        widgets = {
            'country': DatalistWidget(datalist=Country.objects.values_list('name', flat=True)),
            'city': DatalistWidget(datalist=City.objects.values_list('name', flat=True))
        }

    def clean(self):
        cleaned_data = super().clean()

        country_str = cleaned_data.get('country', '')
        city_str = cleaned_data.get('city', '')

        if country_str:
            country = Country.objects.filter(name=country_str).first()
            if country:
                if city_str:
                    city = City.objects.filter(name=city_str, country=country).first()
                    if not city:
                        self.add_error('city', _("We can not find city for given country."))
            else:
                self.add_error('country', _("There is no such country in our database."))

        return cleaned_data


class SubjectForm(forms.ModelForm):

    phone_number = PhoneNumberField(label=_("Phone number"), required=False)
    phone_number_alternative = PhoneNumberField(label=_("Alternative phone number"), required=False)

    # fields required for the address
    country = forms.CharField(required=False)
    city = forms.CharField(required=False)
    zip_code = forms.CharField(required=False)
    street = forms.CharField(required=False)
    house_number = forms.CharField(required=False)
    additional_information = forms.CharField(required=False)

    class Meta:
        model = Subject
        exclude = ('address',)

        widgets = {
            'city': DatalistWidget(datalist=City.objects.values_list('name', flat=True)),
            'country': DatalistWidget(datalist=Country.objects.values_list('name', flat=True)),
            'phone_number': PhoneNumberInternationalFallbackWidget(
                attrs={'placeholder': _('Phone (ex. +4917693333333)')}),
            'phone_number_alternative': PhoneNumberInternationalFallbackWidget(
                attrs={'placeholder': _('Alternative phone (ex. +4917693333333)')}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.address:
            self.fields['country'].initial = self.instance.address.city.country
            self.fields['city'].initial = self.instance.address.city.name
            self.fields['zip_code'].initial = self.instance.address.zip_code
            self.fields['street'].initial = self.instance.address.street
            self.fields['house_number'].initial = self.instance.address.house_number
            self.fields['additional_information'].initial = \
                self.instance.address.additional_information

    def clean(self):
        cleaned_data = super().clean()

        country = cleaned_data.get('country', '')
        city = cleaned_data.get('city', '')
        zip_code = cleaned_data.get('zip_code', '')
        street = cleaned_data.get('street', '')
        house_number = cleaned_data.get('house_number', '')
        add_info = cleaned_data.get('additional_information', '')
        phone_number = cleaned_data.get('phone_number', '')
        email = cleaned_data.get('email', '')

        if any([country, city, zip_code, street, house_number, add_info]):
            af = AddressForm(data=cleaned_data)
            if not af.is_valid():
                if af.errors:
                    for field, errors in af.errors.items():
                        self.add_error(field, errors)

                raise ValidationError(_("Provide more details for the address."))
        else:
            if not any([phone_number, email]):
                raise ValidationError(_("Either email, phone number"
                                        " or address should be provided."))

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
