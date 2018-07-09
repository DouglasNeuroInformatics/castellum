import pytest

from subject_management.forms import SubjectForm


def test_subject_form_empty():
    form = SubjectForm()
    assert form.is_valid() is False


def test_subject_form_with_data_except_email_phone_address(subject_data):
    form = SubjectForm(data=subject_data)
    assert form.is_valid() is False


@pytest.mark.django_db
@pytest.mark.parametrize('email, phone_number', [
    ('t@g.com', '+4917691233434'),
    ('t@g.com', ''),
    ('', '+4917691233434'),
])
def test_subject_form_without_address(subject_data, email, phone_number):

    subject_data.update({
        'address': '',
        'email': email,
        'phone_number': phone_number
    })

    form = SubjectForm(data=subject_data)

    assert form.is_valid() is True


@pytest.mark.django_db
@pytest.mark.parametrize('email, phone_number', [
    ('t@g.com', '+4917691233434'),
    ('t@g.com', ''),
    ('', '+4917691233434'),
])
def test_subject_form_with_address(subject_data, address, email, phone_number):

    subject_data.update({
        'address': address.id,
        'email': email,
        'phone_number': phone_number
    })

    form = SubjectForm(data=subject_data)

    assert form.is_valid() is True
