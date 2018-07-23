import pytest

from subject_management.forms import SubjectForm, AddressForm


def test_subject_form_empty():
    form = SubjectForm()
    assert form.is_valid() is False


def test_subject_form_with_subject_data_except_email_phone_address(subject_data):
    form = SubjectForm(data=subject_data)
    assert form.is_valid() is False


@pytest.mark.django_db
@pytest.mark.parametrize('email, phone_number', [
    ('t@g.com', '+4917691233434'),
    ('t@g.com', ''),
    ('', '+4917691233434'),
])
def test_subject_form_with_email_or_phonenumber_without_address(subject_data, email, phone_number):

    subject_data.update({
        'email': email,
        'phone_number': phone_number,
    })

    form = SubjectForm(data=subject_data)

    assert form.is_valid() is True


@pytest.mark.django_db
@pytest.mark.parametrize('email, phone_number', [
    ('t@g.com', '+4917691233434'),
    ('t@g.com', ''),
    ('', '+4917691233434'),
])
def test_subject_form_with_email_or_phonenumber_with_full_address(full_data,
                                                                  email, phone_number):
    full_data.update({
        'email': email,
        'phone_number': phone_number
    })

    form = SubjectForm(data=full_data)

    assert form.is_valid() is True


@pytest.mark.django_db
def test_subject_form_without_email_or_phonenumber_with_full_address(full_data):

    form = SubjectForm(data=full_data)

    assert form.is_valid() is True


@pytest.mark.django_db
def test_subject_form_without_email_or_phonenumber_with_incomplete_address(subject_data, address):

    subject_data.update({
        'country': address.city.country.name,
        'city': address.city.name,
    })

    form = SubjectForm(data=subject_data)

    assert 'Provide more details for the address' in str(form.errors)
    assert form.is_valid() is False


@pytest.mark.django_db
def test_address_form_given_city_has_no_relation_to_given_country(address_data):

    address_data.update({'city': 'AnyFakeCityName'})
    form = AddressForm(data=address_data)

    assert 'We can not find city for given country.' in str(form.errors)
    assert form.is_valid() is False


@pytest.mark.django_db
def test_address_form_given_country_not_in_db(address_data):

    address_data.update({'country': 'AnyFakeCountryName'})
    form = AddressForm(data=address_data)

    assert 'There is no such country in our database.' in str(form.errors)
    assert form.is_valid() is False


@pytest.mark.django_db
def test_subject_form_subject_is_saved_correctly(full_data, address):

    full_data.update({
        'email': 't@g.com',
        'phone_number': '+4917691232323',
        'phone_number_alternative': '',
    })

    form = SubjectForm(data=full_data)
    assert form.is_valid() is True

    subject = form.save()
    assert subject.address.city.country.name == address.city.country.name
    assert subject.address.city.name == address.city.name
    assert subject.address.zip_code == address.zip_code
    assert subject.address.street == address.street
    assert subject.address.house_number == address.house_number
    assert subject.address.additional_information == address.additional_information
    assert subject.email == 't@g.com'
    assert subject.phone_number == '+4917691232323'
    assert subject.phone_number_alternative == ''


@pytest.mark.django_db
def test_subject_form_init_address_from_subject_instance(subject, address):

    form = SubjectForm(instance=subject)

    assert form.fields['city'].initial == address.city.name
    assert form.fields['zip_code'].initial == address.zip_code
    assert form.fields['street'].initial == address.street
    assert form.fields['house_number'].initial == address.house_number
    assert form.fields['additional_information'].initial == address.additional_information


@pytest.mark.django_db
def test_subject_form_update_city_country_for_existing_instance_address(subject, city, full_data):

    full_data.update({
        'city': city.name,
        'country': city.country.name,
        'email': 't@g.com',
        'phone_number': '+4917691232323',
        'phone_number_alternative': '',
    })

    form = SubjectForm(instance=subject, data=full_data)
    assert form.is_valid() is True

    updated_subject = form.save()
    assert updated_subject.address.city.name == city.name
