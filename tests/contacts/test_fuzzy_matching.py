import pytest
from model_mommy import mommy

from castellum.contacts.models import Contact

import datetime


DATE_OF_BIRTH = datetime.datetime(1970, 1, 1)
FIRST_NAME = 'Eve'


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

    # more than one category
    ('Meier Schmidt', 'Mayer', True),
    ('Meier Schmidt', 'Mier', True),
    ('Sassen Schmidt', 'Saaßen', True),

    # not matches
    ('Meier', 'Schulze', False),
    ('Meier', 'Michel', False),
))
def test_fuzzy_filter(right, wrong, expected):
    contact = mommy.make(
        Contact, first_name=FIRST_NAME, last_name=right, date_of_birth=DATE_OF_BIRTH)
    matches = Contact.objects.fuzzy_filter(FIRST_NAME, wrong, DATE_OF_BIRTH)
    if expected:
        assert contact in matches
    else:
        assert contact not in matches
