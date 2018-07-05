import pytest
from subject_management.forms import SubjectForm


def test_subject_empty_form():
    form = SubjectForm()
    assert form.is_valid() is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    'first_name, last_name, title, gender, birthday, address, email, phone_number, '
    'phone_number_alternative, validity',
    [('alex', 'tyapkov', 'Dr.', 'm', '2010-01-28', 1, 't@g.com',
      '+4917691233434', '+4917691233435', True),
     ('alex', 'tyapkov', 'Dr.', 'm', '2010-01-28', None, 't@g.com', '', '', False),
     ])
def test_subject_form(first_name, last_name, title, gender, birthday,
                      address, email, phone_number, phone_number_alternative, validity):
    form = SubjectForm(data={
        'first_name': first_name,
        'last_name': last_name,
        'title': title,
        'gender': gender,
        'birthday': birthday,
        'address_id': address,
        'email': email,
        'phone_number': phone_number,
        'phone_number_alternative': phone_number_alternative
    })

    assert form.is_valid() is validity
