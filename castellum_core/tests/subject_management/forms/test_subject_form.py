import pytest
from subject_management.forms import SubjectForm


check_data_without_address = [
                ('t@g.com', '+4917691233434', True),
                ('t@g.com', '', True),
                ('', '+4917691233434', True),
                ('', '', False),
              ]

check_data_with_address = [
    ('t@g.com', '+4917691233434', True),
    ('t@g.com', '', True),
    ('', '+4917691233434', True),
    ('', '', True),
    ]


def test_subject_form_empty():
    form = SubjectForm()
    assert form.is_valid() is False


def test_subject_form_with_data_except_email_phone_address(stable_data):
    form = SubjectForm(data={
        'first_name': stable_data['first_name'],
        'last_name': stable_data['last_name'],
        'title': stable_data['title'],
        'gender': stable_data['gender'],
        'birthday': stable_data['birthday'],
        'phone_number_alternative': stable_data['phone_number_alternative']
    })

    assert form.is_valid() is False


@pytest.mark.django_db
@pytest.mark.parametrize('email, phone_number, validity', check_data_without_address)
def test_subject_form_without_address(stable_data, email, phone_number, validity):

    form = SubjectForm(data={
        'first_name': stable_data['first_name'],
        'last_name': stable_data['last_name'],
        'title': stable_data['title'],
        'gender': stable_data['gender'],
        'birthday': stable_data['birthday'],
        'phone_number_alternative': stable_data['phone_number_alternative'],
        'address': '',
        'email': email,
        'phone_number': phone_number,

    })

    assert form.is_valid() is validity


@pytest.mark.django_db
@pytest.mark.parametrize('email, phone_number, validity', check_data_with_address)
def test_subject_form_with_address(stable_data, address, email, phone_number, validity):

    form = SubjectForm(data={
        'first_name': stable_data['first_name'],
        'last_name': stable_data['last_name'],
        'title': stable_data['title'],
        'gender': stable_data['gender'],
        'birthday': stable_data['birthday'],
        'phone_number_alternative': stable_data['phone_number_alternative'],
        'address': address.id,
        'email': email,
        'phone_number': phone_number,

    })

    assert form.is_valid() is validity
