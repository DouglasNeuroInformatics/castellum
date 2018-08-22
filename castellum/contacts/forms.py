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

from .models import Address
from .models import City
from .models import Contact
from .models import Country


class DatalistWidget(TextInput):
    template_name = 'contacts/widgets/datalist.html'

    def __init__(self, *args, datalist=[], **kwargs):
        self.datalist = datalist
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['list'] = context['widget']['attrs']['id'] + '_list'
        context['datalist'] = self.datalist
        return context


class AddressForm(forms.ModelForm):

    country = forms.CharField(max_length=64, widget=DatalistWidget(
        datalist=Country.objects.values_list('name', flat=True)))
    city = forms.CharField(max_length=128, widget=DatalistWidget(
        datalist=City.objects.values_list('name', flat=True)))

    class Meta:
        model = Address
        exclude = ('city',)


class ContactForm(forms.ModelForm):

    # fields required for the address
    country = forms.CharField(label=_('country'), required=False, widget=DatalistWidget(
        datalist=Country.objects.values_list('name', flat=True)))
    city = forms.CharField(label=_('city'), required=False, widget=DatalistWidget(
        datalist=City.objects.values_list('name', flat=True)))
    zip_code = forms.CharField(label=_('zip code'), required=False)
    street = forms.CharField(label=_('street'), required=False)
    house_number = forms.CharField(label=_('house number'), required=False)
    additional_information = forms.CharField(
        label=_('additional address information'), required=False)

    class Meta:
        model = Contact
        exclude = ('address',)

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
        preferred_contact_method = cleaned_data.get('preferred_contact_method', '')

        contact_methods = Contact.CONTACT_METHODS

        if any([country, city, zip_code, street, house_number, add_info]):
            address_form = AddressForm(data=cleaned_data)
            if not address_form.is_valid():

                if address_form.errors:
                    for field, errors in address_form.errors.items():
                        self.add_error(field, errors)

                if preferred_contact_method == dict(contact_methods).get('postal'):
                    self.add_error('preferred_contact_method',
                                   _("Chosen contact method can not be saved."))

                raise ValidationError(_("Provide more details for the address."))

        else:
            if not any([phone_number, email]):
                raise ValidationError(_("Either email, phone number"
                                        " or address should be provided."))

        if not phone_number and preferred_contact_method == dict(contact_methods).get('phone'):
            self.add_error('preferred_contact_method', _("Chosen contact method can not be saved."))
        if not email and preferred_contact_method == dict(contact_methods).get('email'):
            self.add_error('preferred_contact_method', _("Chosen contact method can not be saved."))

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

            if not self.cleaned_data.get('city') and contact.address:
                contact.address.delete()

        return contact
