import pytest
from model_bakery import baker

from castellum.contacts.models import Contact


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
def test_phonetic_matching(right, wrong, expected):
    baker.make(Contact, first_name='Eve', last_name=right)
    matches = Contact.objects.fuzzy_filter('Eve ' + wrong).exists()
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
def test_double_names(first, last, query):
    baker.make(Contact, first_name=first, last_name=last)
    qs = Contact.objects.fuzzy_filter(query)
    assert qs.exists()


@pytest.mark.django_db
def test_only_phone():
    search = '030123456789'
    baker.make(
        Contact, first_name='Eve', last_name='Meier', phone_number='030123456789'
    )
    assert Contact.objects.fuzzy_filter(search).exists()


@pytest.mark.django_db
def test_only_phone_different_formatting():
    search = '+4930-123456789'
    baker.make(
        Contact, first_name='Eve', last_name='Meier', phone_number='030123456789'
    )
    assert Contact.objects.fuzzy_filter(search).exists()


@pytest.mark.django_db
def test_only_mail():
    search = 'test@example.com'
    baker.make(Contact, first_name='Eve', last_name='Meier', email='test@example.com')
    assert Contact.objects.fuzzy_filter(search).exists()


@pytest.mark.django_db
def test_one_component_wrong():
    search = 'test@example.com Shenavar Meier 030123456789'
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
    assert not Contact.objects.fuzzy_filter(search).exists()


@pytest.mark.django_db
def test_right_mail_right_namepart():
    search = 'test@example.com Eve'
    baker.make(Contact, first_name='Eve', last_name='Meier', email='test@example.com')
    assert Contact.objects.fuzzy_filter(search).exists()


@pytest.mark.django_db
def test_only_first_name():
    search = 'Eve'
    baker.make(Contact, first_name='Eve', last_name='Meier', email='test@example.com')
    assert not Contact.objects.fuzzy_filter(search).exists()


@pytest.mark.django_db
def test_excessive_whitespace():
    search = 'Eve        Meier  '
    baker.make(Contact, first_name='Eve', last_name='Meier', email='test@example.com')
    assert Contact.objects.fuzzy_filter(search).exists()


@pytest.mark.django_db
def test_every_input_must_match():
    search = 'test@example.com second@example.com'
    baker.make(Contact, first_name='Eve', last_name='Meier', email='test@example.com')
    assert not Contact.objects.fuzzy_filter(search).exists()


@pytest.mark.django_db
def test_legal_representative_email():
    search = 'test@example.com'
    legal_representative = baker.make(Contact, email='test@example.com')
    baker.make(Contact, legal_representatives=[legal_representative])
    assert Contact.objects.fuzzy_filter(search).count() == 2


@pytest.mark.django_db
def test_legal_representative_phone():
    search = '030123456789'
    legal_representative = baker.make(Contact, phone_number='030123456789')
    baker.make(Contact, legal_representatives=[legal_representative])
    assert Contact.objects.fuzzy_filter(search).count() == 2
