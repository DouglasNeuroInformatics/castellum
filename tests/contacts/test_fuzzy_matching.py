import pytest

from castellum.contacts.models import Contact
from castellum.contacts.views import get_matches

FIRST_NAME = 'Eve'
BIRTHDAY = '1970-01-01'


@pytest.mark.django_db
@pytest.mark.parametrize('right,wrong,expected', (
    # phonetic
    ('Meier', 'Mayer', True),
    ('Schmidt', 'Schmitt', True),

    # combinations
    ('Meier Schmidt', 'Mayer', True),
    ('Meier-Schmidt', 'Mayer', True),

    # typos
    ('Meier', 'Neier', True),
    ('Meier', 'Mier', True),

    # not matches
    ('Meier', 'Schulze', False),
))
def test_user_expiration_date(right, wrong, expected):
    contact = Contact.objects.create(first_name=FIRST_NAME, last_name=right, birthday=BIRTHDAY)
    matches = list(get_matches(FIRST_NAME, wrong, BIRTHDAY))
    if expected:
        assert contact in matches
    else:
        assert contact not in matches
