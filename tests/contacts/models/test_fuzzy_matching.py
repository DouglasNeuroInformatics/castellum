import datetime

import pytest
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.contacts.models import PotentialDuplicateError


@pytest.mark.django_db
@pytest.mark.parametrize('right,wrong,expected', (
    # phonetic
    ('Meier', 'Mayer', True),
    ('Schmidt', 'Schmitt', True),
    ('Hoffmann', 'Hofmann', True),
    ('Sassen', 'Saaßen', True),

    # combinations
    ('Meier Schmidt', 'Meier', True),
    ('Meier Schmidt', 'Schmidt', True),
    ('Meier-Schmidt', 'Meier', True),
    ('Meier Schmidt-Mankowski', 'Meier', True),

    # typos
    ('Meier', 'Neier', True),
    ('Meier', 'Mier', True),
    ('Meier', 'MEIER', True),
    ('Meier', 'mEIER', True),
    ('Jäger', 'Jaeger', True),
    ('Böhm', 'B;hm', True),
    ('Jäger', "J'ger", True),
    ('Müller', 'M[ller', True),
    # ('Mayer', 'Mazer', True), # fails
    # ('Meier', 'Mei er', True), # fails
    # ('Meier', 'Meiek', True),  # fails

    # diacritics
    ('Gerçeği', 'Gercegi', True),
    ('Mašoník', 'Masonik', True),

    # more than one category
    ('Meier Schmidt', 'Mayer', True),
    ('Meier Schmidt', 'Mier', True),
    ('Sassen Schmidt', 'Saaßen', True),

    # not matches
    ('Meier', 'Schulze', False),
    ('Meier', 'Michel', False),
))
def test_search_phonetic_matching(right, wrong, expected):
    baker.make(Contact, first_name='Eve', last_name=right)
    matches = Contact.objects.search(f'Eve {wrong}').exists()
    assert matches == expected


@pytest.mark.django_db
@pytest.mark.parametrize('first,last,query', [
    ('Else', 'Lasker Schüler', 'Else Lasker Schüler'),
    ('Else', 'Lasker-Schüler', 'Else Lasker Schüler'),
    ('Else', 'Lasker Schüler', 'Else Lasker-Schüler'),
    ('Else', 'Lasker Schüler', 'Else Lasker'),
    ('Else', 'Lasker Schüler', 'Else Schüler'),

    ('Alfred Jodocus', 'Kwak', 'Alfred Jodocus Kwak'),
    ('Alfred-Jodocus', 'Kwak', 'Alfred Jodocus Kwak'),
    ('Alfred Jodocus', 'Kwak', 'Alfred-Jodocus Kwak'),
    ('Alfred Jodocus', 'Kwak', 'Alfred Kwak'),
    ('Alfred Jodocus', 'Kwak', 'Jodocus Kwak'),

    # every input must match some part of the data, so the following
    # cases would fail
    # ('Else', 'Lasker', 'Else Lasker Schüler'),
    # ('Else', 'Schüler', 'Else Lasker Schüler'),
    # ('Alfred', 'Kwak', 'Alfred Jodocus Kwak'),
    # ('Jodocus', 'Kwak', 'Alfred Jodocus Kwak'),
])
def test_search_double_names(first, last, query):
    baker.make(Contact, first_name=first, last_name=last)
    qs = Contact.objects.search(query)
    assert qs.exists()


@pytest.mark.django_db
def test_search_only_phone():
    query = '030123456789'
    baker.make(
        Contact, first_name='Eve', last_name='Meier', phone_number='030123456789'
    )
    assert Contact.objects.search(query).exists()


@pytest.mark.django_db
def test_search_only_phone_different_formatting():
    query = '+4930-123456789'
    baker.make(
        Contact, first_name='Eve', last_name='Meier', phone_number='030123456789'
    )
    assert Contact.objects.search(query).exists()


@pytest.mark.django_db
def test_search_only_mail():
    query = 'test@example.com'
    baker.make(Contact, first_name='Eve', last_name='Meier', email='test@example.com')
    assert Contact.objects.search(query).exists()


@pytest.mark.django_db
def test_search_one_component_wrong():
    query = 'test@example.com Shenavar Meier 030123456789'
    baker.make(
        Contact,
        first_name='Eve',
        last_name='Meier',
        email='test@example.com',
        phone_number='030123456789'
    )
    baker.make(
        Contact,
        first_name='Shenavar',
        last_name='Meier',
        email='wrong@example.com',
        phone_number='030123456789'
    )
    baker.make(
        Contact,
        first_name='Shenavar',
        last_name='Meier',
        email='test@example.com',
        phone_number='030777777777'
    )
    assert not Contact.objects.search(query).exists()


@pytest.mark.django_db
def test_search_right_mail_right_namepart():
    query = 'test@example.com Eve'
    baker.make(Contact, first_name='Eve', last_name='Meier', email='test@example.com')
    assert Contact.objects.search(query).exists()


@pytest.mark.django_db
def test_search_only_first_name():
    query = 'Eve'
    baker.make(Contact, first_name='Eve', last_name='Meier', email='test@example.com')
    assert not Contact.objects.search(query).exists()


@pytest.mark.django_db
def test_search_excessive_whitespace():
    query = 'Eve        Meier  '
    baker.make(Contact, first_name='Eve', last_name='Meier', email='test@example.com')
    assert Contact.objects.search(query).exists()


@pytest.mark.django_db
def test_search_every_input_must_match():
    query = 'test@example.com second@example.com'
    baker.make(Contact, first_name='Eve', last_name='Meier', email='test@example.com')
    assert not Contact.objects.search(query).exists()


@pytest.mark.django_db
def test_search_legal_representative_email():
    query = 'test@example.com'
    legal_representative = baker.make(Contact, email='test@example.com')
    baker.make(Contact, legal_representatives=[legal_representative])
    assert Contact.objects.search(query).count() == 2


@pytest.mark.django_db
def test_search_legal_representative_phone():
    query = '030123456789'
    legal_representative = baker.make(Contact, phone_number='030123456789')
    baker.make(Contact, legal_representatives=[legal_representative])
    assert Contact.objects.search(query).count() == 2


@pytest.mark.django_db
def test_fuzzy_find_exact_date_of_birth():
    date = datetime.date(1970, 1, 1)
    baker.make(Contact, first_name='foo', last_name='bar', date_of_birth=date)
    assert Contact.objects.fuzzy_find('foo', 'bar', date)


@pytest.mark.django_db
def test_fuzzy_find_exact_email():
    baker.make(Contact, first_name='foo', last_name='bar', email='foo@example.com')
    assert Contact.objects.fuzzy_find('foo', 'bar', emails=['foo@example.com'])


@pytest.mark.django_db
def test_fuzzy_find_exact_phone_number():
    baker.make(Contact, first_name='foo', last_name='bar', phone_number='030123456')
    assert Contact.objects.fuzzy_find('foo', 'bar', phone_numbers=['030123456'])


@pytest.mark.django_db
def test_fuzzy_find_exact_phone_number_alternative():
    baker.make(Contact, first_name='foo', last_name='bar', phone_number_alternative='030123456')  # noqa
    assert Contact.objects.fuzzy_find('foo', 'bar', phone_numbers=['030123456'])


@pytest.mark.django_db
def test_fuzzy_find_exact_legal_representative_of(contact):
    c = baker.make(Contact, first_name='foo', last_name='bar', legal_representative_of=[contact])  # noqa
    assert Contact.objects.fuzzy_find('foo', 'bar', legal_representative_of=[contact])


@pytest.mark.django_db
def test_fuzzy_find_potential_first_name_extra():
    date = datetime.date(1970, 1, 1)
    baker.make(Contact, first_name='foo baz', last_name='bar', date_of_birth=date)
    with pytest.raises(PotentialDuplicateError):
        Contact.objects.fuzzy_find('foo', 'bar', date)


@pytest.mark.django_db
def test_fuzzy_find_potential_first_name_missing():
    date = datetime.date(1970, 1, 1)
    baker.make(Contact, first_name='foo', last_name='bar', date_of_birth=date)
    with pytest.raises(PotentialDuplicateError):
        Contact.objects.fuzzy_find('foo baz', 'bar', date)


@pytest.mark.django_db
def test_fuzzy_find_potential_first_name_title():
    date = datetime.date(1970, 1, 1)
    baker.make(Contact, first_name='Dr.', last_name='bar', date_of_birth=date)
    with pytest.raises(PotentialDuplicateError):
        Contact.objects.fuzzy_find('foo', 'bar', date_of_birth=date)


@pytest.mark.django_db
def test_fuzzy_find_potential_last_name():
    date = datetime.date(1970, 1, 1)
    baker.make(Contact, first_name='foo', last_name='bar', date_of_birth=date)
    with pytest.raises(PotentialDuplicateError):
        Contact.objects.fuzzy_find('foo', 'baz', date)


@pytest.mark.django_db
def test_fuzzy_find_potential_date_of_birth_typo():
    baker.make(Contact, first_name='foo', last_name='bar', date_of_birth=datetime.date(1970, 10, 1))  # noqa
    with pytest.raises(PotentialDuplicateError):
        Contact.objects.fuzzy_find('foo', 'bar', datetime.date(1970, 1, 1))


@pytest.mark.django_db
def test_fuzzy_find_potential_date_of_birth_missing():
    baker.make(Contact, first_name='foo', last_name='bar')
    with pytest.raises(PotentialDuplicateError):
        Contact.objects.fuzzy_find('foo', 'bar', datetime.date(1970, 1, 1))


@pytest.mark.django_db
def test_fuzzy_find_potential_twins():
    date = datetime.date(1941, 1, 1)
    baker.make(Contact, first_name='Hanni', last_name='Sullivan', date_of_birth=date, email='test@example.com')  # noqa
    with pytest.raises(PotentialDuplicateError):
        Contact.objects.fuzzy_find('Nanni', 'Sullivan', date, emails=['test@example.com'])  # noqa


@pytest.mark.django_db
def test_fuzzy_find_none_name():
    baker.make(Contact, first_name='foo', last_name='bar', date_of_birth=datetime.date(1970, 1, 1))  # noqa
    assert Contact.objects.fuzzy_find('asd', '123', datetime.date(1970, 1, 1)) is None


@pytest.mark.django_db
def test_fuzzy_find_none_date_of_birth():
    baker.make(Contact, first_name='foo', last_name='bar', date_of_birth=datetime.date(1970, 1, 1))  # noqa
    assert Contact.objects.fuzzy_find('foo', 'bar', datetime.date(2003, 12, 13)) is None

