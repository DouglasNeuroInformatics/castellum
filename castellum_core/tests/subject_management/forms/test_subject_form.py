import pytest
from subject_management.forms import SubjectForm


def test_subject_empty_form():
    form = SubjectForm()
    assert form.is_valid() is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    'first_name, last_name, title, gender, birthday, email, phone_number, '
    'phone_number_alternative, validity',
    [('a', 't', 'Dr.', 'm', '2010-01-28', 't@g.com',
      '+4917691233434', '+4917691233435', True),
     ('a', 't', 'Dr.', 'm', '2010-01-28', '', '', '', False),
     ('a', 't', 'Dr.', 'm', '2010-01-28', 't@m.com', '', '', True),
     ('a', 't', 'Dr.', 'm', '2010-01-28', '', '+4917692343434', '', True),
     ])
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
    'first_name, last_name, title, gender, birthday, email, phone_number, '
    'phone_number_alternative, validity',
    [('a', 't', 'Dr.', 'm', '2010-01-28', 't@g.com',
      '+4917691233434', '+4917691233435', True),
     ('a', 't', 'Dr.', 'm', '2010-01-28', '', '', '', True),
     ])
def test_subject_form_with_address(address, first_name, last_name, title, gender, birthday,
                      email, phone_number, phone_number_alternative, validity):

    address.id = 1
    print(address.id)
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
