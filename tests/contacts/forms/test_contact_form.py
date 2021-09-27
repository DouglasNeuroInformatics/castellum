import datetime

import pytest

from castellum.contacts.forms import AddressForm
from castellum.contacts.forms import ContactForm
from castellum.contacts.models import Address


def test_empty_contact_form(user):
    form = ContactForm(user=user)
    assert form.is_valid() is False


@pytest.mark.django_db
@pytest.mark.parametrize('email, phone_number', [
    ('t@g.com', '+4917691233434'),
    ('t@g.com', ''),
    ('', '+4917691233434'),
])
def test_contact_form_with_email_or_phonenumber_without_address(
    user, contact_data, email, phone_number
):
    contact_data.update({
        'email': email,
        'phone_number': phone_number,
    })

    form = ContactForm(user=user, data=contact_data)

    assert form.is_valid() is True


@pytest.mark.django_db
@pytest.mark.parametrize('email, phone_number', [
    ('t@g.com', '+4917691233434'),
    ('t@g.com', ''),
    ('', '+4917691233434'),
])
def test_contact_form_with_email_or_phonenumber_with_full_address(
    user, full_data, email, phone_number
):
    full_data.update({
        'email': email,
        'phone_number': phone_number,
    })

    form = ContactForm(user=user, data=full_data)

    assert form.is_valid() is True


@pytest.mark.django_db
def test_contact_form_without_email_or_phonenumber_with_full_address(user, full_data):
    form = ContactForm(user=user, data=full_data)

    assert form.is_valid() is True


@pytest.mark.django_db
def test_contact_form_without_email_or_phonenumber_with_incomplete_address(
    user, contact_data, address
):
    contact_data.update({
        'country': address.country,
        'city': address.city,
    })

    form = ContactForm(user=user, data=contact_data)

    assert 'Provide more details for the address' in str(form.errors)
    assert form.is_valid() is False


@pytest.mark.django_db
def test_address_form_given_country_not_in_db(user, address_data):
    address_data.update({'country': 'AnyFakeCountryName'})
    form = AddressForm(data=address_data)

    assert form.is_valid() is True


@pytest.mark.django_db
def test_contact_form_contact_is_saved_correctly(user, full_data, address):
    full_data.update({
        'email': 't@g.com',
        'phone_number': '+4917691232323',
        'phone_number_alternative': '',
    })

    form = ContactForm(user=user, data=full_data)
    assert form.is_valid() is True

    contact = form.save()
    assert contact.address.country == address.country
    assert contact.address.city == address.city
    assert contact.address.zip_code == address.zip_code
    assert contact.address.street == address.street
    assert contact.address.house_number == address.house_number
    assert contact.address.additional_information == address.additional_information
    assert contact.email == 't@g.com'
    assert contact.phone_number == '+4917691232323'
    assert contact.phone_number_alternative == ''


@pytest.mark.django_db
def test_contact_form_update_city_country_for_existing_instance_address(user, contact, full_data):
    city = 'foo'
    country = 'bar'

    full_data.update({
        'city': city,
        'country': country,
        'email': 't@g.com',
        'phone_number': '+4917691232323',
        'phone_number_alternative': '',
    })

    form = ContactForm(user=user, instance=contact, data=full_data)
    assert form.is_valid() is True

    updated_contact = form.save()
    assert updated_contact.address.city == city


@pytest.mark.django_db
def test_contact_form_delete_existing_address_if_empty(user, contact, contact_data):
    contact_data.update({
        'phone_number': '+4917691232323',
        'phone_number_alternative': '',
    })

    address_count_before = Address.objects.count()

    form = ContactForm(user=user, instance=contact, data=contact_data)
    form.save()

    assert Address.objects.count() == address_count_before - 1


@pytest.mark.django_db
@pytest.mark.parametrize('method', [
    ('postal'),
    ('email'),
    ('phone'),
])
def test_contact_form_without_data_with_preferred_contact_method(user, contact_data, method):
    contact_data.update({
        'preferred_contact_method': method,
    })

    form = ContactForm(user=user, data=contact_data)

    assert form.is_valid() is False


def test_contact_form_with_email_and_preferred_contact_method(user, contact_data):
    contact_data.update({
        'email': 't@g.com',
        'preferred_contact_method': 'email',
    })

    form = ContactForm(user=user, data=contact_data)

    assert form.is_valid() is True


def test_contact_form_with_email_and_wrong_preferred_contact_method(user, contact_data):
    contact_data.update({
        'email': 't@g.com',
        'preferred_contact_method': 'phone',
    })

    form = ContactForm(user=user, data=contact_data)

    assert form.is_valid() is False


def test_contact_form_with_phone_and_preferred_contact_method(user, contact_data):
    contact_data.update({
        'phone_number': '+4917691232323',
        'preferred_contact_method': 'phone',
    })

    form = ContactForm(user=user, data=contact_data)

    assert form.is_valid() is True


def test_contact_form_with_phone_and_wrong_preferred_contact_method(user, contact_data):
    contact_data.update({
        'phone_number': '+4917691232323',
        'preferred_contact_method': 'email',
    })

    form = ContactForm(user=user, data=contact_data)

    assert form.is_valid() is False


@pytest.mark.django_db
def test_contact_form_with_address_and_preferred_contact_method(user, full_data):
    full_data.update({
        'preferred_contact_method': 'postal',
    })

    form = ContactForm(user=user, data=full_data)

    assert form.is_valid() is True


@pytest.mark.django_db
def test_contact_form_with_address_and_wrong_preferred_contact_method(user, full_data):
    full_data.update({
        'preferred_contact_method': 'email',
    })

    form = ContactForm(user=user, data=full_data)

    assert form.is_valid() is False


@pytest.mark.django_db
def test_contact_form_with_legal_representatives_add(user, full_data, contact):
    full_data.update({
        'pane': 'guardians',
        'guardians_add': [contact.subject.pk],
    })

    form = ContactForm(user=user, data=full_data)

    assert form.is_valid() is True
    assert form.cleaned_data['guardians_add'].get() == contact.subject
    assert form.cleaned_data['email'] == ''


@pytest.mark.django_db
def test_contact_form_with_legal_representatives_add_privacy_level(user, full_data, contact):
    full_data.update({
        'pane': 'guardians',
        'guardians_add': [contact.subject.pk],
    })

    contact.subject.privacy_level = 2
    contact.subject.save()

    form = ContactForm(user=user, data=full_data, instance=contact)

    assert form.is_valid() is False
    assert 'Select a valid choice.' in str(form.errors)


@pytest.mark.django_db
def test_contact_form_with_legal_representatives_removes_address(user, full_data):
    form = ContactForm(user=user, data=full_data)
    contact = form.save()
    assert contact.get_address()

    data = {
        **full_data,
        'pane': 'guardians',
        'guardians_add': [contact.subject.pk],
    }

    form = ContactForm(user=user, instance=contact, data=data)
    contact = form.save()
    assert not contact.get_address()


@pytest.mark.django_db
def test_contact_form_with_legal_representatives_remove(user, full_data, contact):
    full_data.update({
        'pane': 'guardians',
        'guardians_remove': [contact.subject.pk],
    })

    contact.legal_representatives.add(contact)

    form = ContactForm(user=user, data=full_data, instance=contact)

    assert form.is_valid() is True
    assert form.cleaned_data['guardians_remove'].get() == contact.subject


@pytest.mark.django_db
def test_contact_form_underage_without_legal_representative(user, full_data):
    msg = 'Subjects under the age of 16 need a legal representative.'
    full_data.update({
        'date_of_birth': '{}-01-01'.format(datetime.date.today().year),
    })

    form = ContactForm(user=user, data=full_data)

    assert form.is_valid() is False
    assert msg in str(form.errors)
