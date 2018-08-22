import pytest

from castellum.contacts.forms import ContactForm, AddressForm
from castellum.contacts.models import Address


def test_contact_form_empty():
    form = ContactForm()
    assert form.is_valid() is False


def test_contact_form_with_contact_data_except_email_phone_address(contact_data):
    form = ContactForm(data=contact_data)
    assert form.is_valid() is False
    assert 'Either email, phone number or address should be provided.' in str(form.errors)


@pytest.mark.django_db
@pytest.mark.parametrize('email, phone_number', [
    ('t@g.com', '+4917691233434'),
    ('t@g.com', ''),
    ('', '+4917691233434'),
])
def test_contact_form_with_email_or_phonenumber_without_address(contact_data, email, phone_number):

    contact_data.update({
        'email': email,
        'phone_number': phone_number,
    })

    form = ContactForm(data=contact_data)

    assert form.is_valid() is True


@pytest.mark.django_db
@pytest.mark.parametrize('email, phone_number', [
    ('t@g.com', '+4917691233434'),
    ('t@g.com', ''),
    ('', '+4917691233434'),
])
def test_contact_form_with_email_or_phonenumber_with_full_address(full_data,
                                                                  email, phone_number):
    full_data.update({
        'email': email,
        'phone_number': phone_number
    })

    form = ContactForm(data=full_data)

    assert form.is_valid() is True


@pytest.mark.django_db
def test_contact_form_without_email_or_phonenumber_with_full_address(full_data):

    form = ContactForm(data=full_data)

    assert form.is_valid() is True


@pytest.mark.django_db
def test_contact_form_without_email_or_phonenumber_with_incomplete_address(contact_data, address):

    contact_data.update({
        'country': address.city.country.name,
        'city': address.city.name,
    })

    form = ContactForm(data=contact_data)

    assert 'Provide more details for the address' in str(form.errors)
    assert form.is_valid() is False


@pytest.mark.django_db
def test_address_form_given_country_not_in_db(address_data):

    address_data.update({'country': 'AnyFakeCountryName'})
    form = AddressForm(data=address_data)

    assert form.is_valid() is True


@pytest.mark.django_db
def test_contact_form_contact_is_saved_correctly(full_data, address):

    full_data.update({
        'email': 't@g.com',
        'phone_number': '+4917691232323',
        'phone_number_alternative': '',
    })

    form = ContactForm(data=full_data)
    assert form.is_valid() is True

    contact = form.save()
    assert contact.address.city.country.name == address.city.country.name
    assert contact.address.city.name == address.city.name
    assert contact.address.zip_code == address.zip_code
    assert contact.address.street == address.street
    assert contact.address.house_number == address.house_number
    assert contact.address.additional_information == address.additional_information
    assert contact.email == 't@g.com'
    assert contact.phone_number == '+4917691232323'
    assert contact.phone_number_alternative == ''


@pytest.mark.django_db
def test_contact_form_init_address_from_contact_instance(contact, address):

    form = ContactForm(instance=contact)

    assert form.fields['city'].initial == address.city.name
    assert form.fields['zip_code'].initial == address.zip_code
    assert form.fields['street'].initial == address.street
    assert form.fields['house_number'].initial == address.house_number
    assert form.fields['additional_information'].initial == address.additional_information


@pytest.mark.django_db
def test_contact_form_update_city_country_for_existing_instance_address(contact, city, full_data):

    full_data.update({
        'city': city.name,
        'country': city.country.name,
        'email': 't@g.com',
        'phone_number': '+4917691232323',
        'phone_number_alternative': '',
    })

    form = ContactForm(instance=contact, data=full_data)
    assert form.is_valid() is True

    updated_contact = form.save()
    assert updated_contact.address.city.name == city.name


@pytest.mark.django_db
def test_contact_form_delete_existing_address_if_empty(contact, contact_data):

    contact_data.update({
        'phone_number': '+4917691232323',
        'phone_number_alternative': '',
    })

    address_count_before = Address.objects.count()

    form = ContactForm(instance=contact, data=contact_data)
    form.save()

    assert Address.objects.count() == address_count_before - 1


@pytest.mark.django_db
@pytest.mark.parametrize('method', [
    ('postal'),
    ('email'),
    ('phone'),
])
def test_contact_form_wihtout_data_with_preferred_contact_method(contact_data, method):

    contact_data.update({
        'preferred_contact_method': method,
    })

    form = ContactForm(data=contact_data)

    assert form.is_valid() is False


def test_contact_form_with_email_and_preferred_contact_method(contact_data):

    contact_data.update({
        'email': 't@g.com',
        'preferred_contact_method': 'email',
    })

    form = ContactForm(data=contact_data)

    assert form.is_valid() is True


def test_contact_form_with_email_and_wrong_preferred_contact_method(contact_data):

    contact_data.update({
        'email': 't@g.com',
        'preferred_contact_method': 'phone',
    })

    form = ContactForm(data=contact_data)

    assert form.is_valid() is False


def test_contact_form_with_phone_and_preferred_contact_method(contact_data):

    contact_data.update({
        'phone_number': '+4917691232323',
        'preferred_contact_method': 'phone',
    })

    form = ContactForm(data=contact_data)

    assert form.is_valid() is True


def test_contact_form_with_phone_and_wrong_preferred_contact_method(contact_data):

    contact_data.update({
        'phone_number': '+4917691232323',
        'preferred_contact_method': 'email',
    })

    form = ContactForm(data=contact_data)

    assert form.is_valid() is False


@pytest.mark.django_db
def test_contact_form_with_address_and_preferred_contact_method(full_data):

    full_data.update({
        'preferred_contact_method': 'postal',
    })

    form = ContactForm(data=full_data)

    assert form.is_valid() is True


@pytest.mark.django_db
def test_contact_form_with_address_and_wrong_preferred_contact_method(full_data):

    full_data.update({
        'preferred_contact_method': 'email',
    })

    form = ContactForm(data=full_data)

    assert form.is_valid() is False
