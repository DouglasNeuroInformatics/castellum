import pytest

from castellum.contacts.models import Contact

FIRST_NAME = 'Eve'
BIRTHDAY = '1970-01-01'


@pytest.mark.django_db
@pytest.mark.parametrize('right,wrong,expected', (
    # phonetic
    ('Meier', 'Mayer', True),
    ('Schmidt', 'Schmitt', True),

    # combinations
    ('Meier Schmidt', 'Meier', True),
    ('Meier Schmidt', 'Schmidt', True),
    ('Meier-Schmidt', 'Meier', True),
    ('Meier Schmidt-Mankowski', 'Meier', True),

    # typos
    ('Meier', 'Neier', True),
    ('Meier', 'Mier', True),
    # ('Meier', 'Meiek', True),  # fails

    # more than one category
    ('Meier Schmidt', 'Mayer', True),
    ('Meier Schmidt', 'Mier', True),

    # not matches
    ('Meier', 'Schulze', False),
    ('Meier', 'Michel', False),
))
def test_fuzzy_filter(right, wrong, expected):
    contact = Contact.objects.create(first_name=FIRST_NAME, last_name=right, birthday=BIRTHDAY)
    matches = Contact.objects.fuzzy_filter(FIRST_NAME, wrong, BIRTHDAY)
    if expected:
        assert contact in matches
    else:
        assert contact not in matches
