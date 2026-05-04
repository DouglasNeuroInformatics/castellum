
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from castellum.contacts.models import BlockHash
from castellum.subjects.models import Consent


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    'data_protection_officer',
])
def test_blocklist_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/blocklist/'
    response = client.get(url)
    assert response.status_code == 200


def test_blocklist_no_match(request, client, user):
    client.force_login(user)
    url = '/subjects/blocklist/'
    response = client.post(url, {
        'first_name': 'Foo',
        'last_name': 'Test',
        'year_of_birth': '1970',
    })
    assert response.status_code == 200
    assert b'No match found' in response.content


def test_blocklist_blocked(request, client, user, subject):
    subject.blocked = True
    subject.save()

    client.force_login(user)
    url = '/subjects/blocklist/'
    response = client.post(url, {
        'first_name': subject.contact.first_name,
        'last_name': subject.contact.last_name,
        'year_of_birth': '1970',
    })
    assert response.status_code == 200
    assert b'We have found a match' in response.content


def test_blocklist_consent_denied(request, client, user, subject):
    baker.make(Consent, subject=subject, document=None)

    client.force_login(user)
    url = '/subjects/blocklist/'
    response = client.post(url, {
        'first_name': subject.contact.first_name,
        'last_name': subject.contact.last_name,
        'year_of_birth': '1970',
    })
    assert response.status_code == 200
    assert b'We have found a match' in response.content


def test_blocklist_block_hash(request, client, user):
    BlockHash.block(first_name='Foo', last_name='Test', year_of_birth=1970)

    client.force_login(user)
    url = '/subjects/blocklist/'
    response = client.post(url, {
        'first_name': 'Foo',
        'last_name': 'Test',
        'year_of_birth': '1970',
    })
    assert response.status_code == 200
    assert b'We have found a match' in response.content


def test_blocklist_block_hash_missing_year(request, client, user):
    BlockHash.block(first_name='Foo', last_name='Test')

    client.force_login(user)
    url = '/subjects/blocklist/'
    response = client.post(url, {
        'first_name': 'Foo',
        'last_name': 'Test',
        'year_of_birth': '1970',
    })
    assert response.status_code == 200
    assert b'We have found a match' in response.content


def test_blocklist_file_view(request, client, user):
    BlockHash.block(first_name='Foo', last_name='Test', year_of_birth=1970)

    csv_in = b"""
first_name,last_name,year_of_birth,extra
Foo,Test,1970,1
Bar,Test,1970,2
""".lstrip()
    csv_out = b"""
first_name,last_name,year_of_birth,extra,is_blocked
Foo,Test,1970,1,yes
Bar,Test,1970,2,no
""".lstrip().replace(b'\n', b'\r\n')

    client.force_login(user)
    url = '/subjects/blocklist/batch/'
    file = SimpleUploadedFile('test.csv', csv_in, content_type='text/csv')
    response = client.post(url, {'file': file})
    assert response.status_code == 200
    assert response.content == csv_out
