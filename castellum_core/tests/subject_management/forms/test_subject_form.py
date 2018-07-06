import pytest

from subject_management.forms import SubjectForm

stable_data = ('a', 't', 'Dr.', 'm', '2010-01-28', '+4917691233435')

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


def test_subject_empty_form():
    form = SubjectForm()
    assert form.is_valid() is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    'first_name, last_name, title, gender, birthday, phone_number_alternative,'
    ' email, phone_number, validity',
    [stable_data + data for data in check_data_without_address])
def test_subject_form_without_address(first_name, last_name, title, gender, birthday,
                                      email, phone_number, phone_number_alternative, validity):

    form = SubjectForm(data={
        'first_name': first_name,
        'last_name': last_name,
        'title': title,
        'gender': gender,
        'birthday': birthday,
        'address': '',
        'email': email,
        'phone_number': phone_number,
        'phone_number_alternative': phone_number_alternative
    })

    assert form.is_valid() is validity


@pytest.mark.django_db
@pytest.mark.parametrize(
    'first_name, last_name, title, gender, birthday, phone_number_alternative, '
    'email, phone_number, validity',
    [stable_data + data for data in check_data_with_address])
def test_subject_form_with_address(address, first_name, last_name, title, gender, birthday,
                                   email, phone_number, phone_number_alternative, validity):

    form = SubjectForm(data={
        'first_name': first_name,
        'last_name': last_name,
        'title': title,
        'gender': gender,
        'birthday': birthday,
        'address': address.id,
        'email': email,
        'phone_number': phone_number,
        'phone_number_alternative': phone_number_alternative
    })

    assert form.is_valid() is validity
