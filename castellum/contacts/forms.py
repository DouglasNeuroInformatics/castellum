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
from django.utils.translation import ugettext_lazy as _

from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentConfirmation
from castellum.subjects.models import Subject
from castellum.utils.forms import DatalistWidget

from .models import Address
from .models import City
from .models import Contact
from .models import Country

DAYS = ['availability_' + day for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']]


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

    # fields required for subject
    privacy_level = Subject._meta.get_field('privacy_level').formfield(widget=forms.RadioSelect)
    note_hard_of_hearing = Subject._meta.get_field('note_hard_of_hearing').formfield()
    note_difficult_to_understand = (
        Subject._meta.get_field('note_difficult_to_understand').formfield()
    )
    note_abusive_language = Subject._meta.get_field('note_abusive_language').formfield()
    availability_monday = Subject._meta.get_field('availability_monday').formfield()
    availability_tuesday = Subject._meta.get_field('availability_tuesday').formfield()
    availability_wednesday = Subject._meta.get_field('availability_wednesday').formfield()
    availability_thursday = Subject._meta.get_field('availability_thursday').formfield()
    availability_friday = Subject._meta.get_field('availability_friday').formfield()
    not_available_until = Subject._meta.get_field('not_available_until').formfield()

    consent_type = ConsentConfirmation._meta.get_field('type').formfield(required=False)
    consent_status = ConsentConfirmation._meta.get_field('status').formfield(required=False)

    class Meta:
        model = Contact
        exclude = ('address',)

    def __init__(self, user, *args, **kwargs):

        self.user = user
        super().__init__(*args, **kwargs)

        if self.instance.address:
            self.fields['country'].initial = self.instance.address.city.country.name
            self.fields['city'].initial = self.instance.address.city.name
            self.fields['zip_code'].initial = self.instance.address.zip_code
            self.fields['street'].initial = self.instance.address.street
            self.fields['house_number'].initial = self.instance.address.house_number
            self.fields['additional_information'].initial = \
                self.instance.address.additional_information

        if self.instance.pseudonym:
            self.fields['privacy_level'].initial = self.instance.subject.privacy_level
            self.fields['note_hard_of_hearing'].initial = self.instance.subject.note_hard_of_hearing
            self.fields['note_difficult_to_understand'].initial = (
                self.instance.subject.note_difficult_to_understand
            )
            self.fields['note_abusive_language'].initial = (
                self.instance.subject.note_abusive_language
            )
            for day in DAYS:
                self.fields[day].initial = getattr(self.instance.subject, day).all()
            self.fields['not_available_until'].initial = self.instance.subject.not_available_until

            consent = self.instance.subject.consent
            if consent and consent.status == 'waiting':
                self.fields['consent_type'].initial = consent.type
                self.fields['consent_status'].initial = consent.status

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

        privacy_level = cleaned_data.get('privacy_level', 0)
        if not self.user.has_privacy_level(privacy_level):
            raise ValidationError(_(
                "Please choose lower privacy level for the subject."),
                code='invalid')

        is_address_data = any([country, city, zip_code, street, house_number, add_info])
        if is_address_data:
            address_form = AddressForm(data=cleaned_data)
            if not address_form.is_valid():
                if address_form.errors:
                    for field, errors in address_form.errors.items():
                        self.add_error(field, errors)

                raise ValidationError(_("Provide more details for the address."), code='invalid')
        else:
            if not any([phone_number, email]):
                raise ValidationError(_("Either email, phone number"
                                        " or address should be provided."), code='invalid')

        if not is_address_data and preferred_contact_method == 'postal':
            self.add_error('preferred_contact_method', _("Chosen contact method can not be saved."))
            self.add_error(None, _("Please provide a complete address."))
        if not phone_number and preferred_contact_method == 'phone':
            self.add_error('preferred_contact_method', _("Chosen contact method can not be saved."))
            self.add_error(None, _("Please provide a phone number."))
        if not email and preferred_contact_method == 'email':
            self.add_error('preferred_contact_method', _("Chosen contact method can not be saved."))
            self.add_error(None, _("Please provide an email."))

        if self.cleaned_data['consent_type'] or self.cleaned_data['consent_status']:
            consent_check = [self.cleaned_data['consent_type'], self.cleaned_data['consent_status']]
            if not all(consent_check):
                raise ValidationError(_("Please, fill out both type and "
                                        "status of the consent."), code='invalid')

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

        if contact.pseudonym:
            contact.subject.privacy_level = self.cleaned_data['privacy_level']
            contact.subject.note_hard_of_hearing = self.cleaned_data['note_hard_of_hearing']
            contact.subject.note_difficult_to_understand = (
                self.cleaned_data['note_difficult_to_understand']
            )
            contact.subject.note_abusive_language = self.cleaned_data['note_abusive_language']
            for day in DAYS:
                getattr(contact.subject, day).set(self.cleaned_data[day])
            contact.subject.not_available_until = self.cleaned_data['not_available_until']
            if commit:
                contact.subject.save()

            consent = contact.subject.consent
            if consent and consent.status == 'waiting':
                if (
                    consent.type != self.cleaned_data['consent_type'] or
                    consent.status != self.cleaned_data['consent_status']
                ):
                    consent.type = self.cleaned_data['consent_type']
                    consent.status = self.cleaned_data['consent_status']
                    consent.save()
            elif self.cleaned_data['consent_type'] or self.cleaned_data['consent_status']:
                ConsentConfirmation.objects.create(
                    type=self.cleaned_data['consent_type'],
                    status=self.cleaned_data['consent_status'],
                    subject=contact.subject,
                    revision=Consent.objects.latest(),
                )

        return contact


class SearchForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'first_name',
            'last_name',
            'date_of_birth',
        ]
