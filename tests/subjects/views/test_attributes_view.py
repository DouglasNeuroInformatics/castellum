
import pytest
from django.conf import settings

from castellum.recruitment.models import Attribute
from castellum.studies.models import StudyType


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_update_200(request, client, user_fixture, subject, attribute):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = f'/subjects/{subject.pk}/attributes/'
    response = client.get(url)
    assert response.status_code == 200
    assert attribute.label.encode(response.charset) in response.content


def test_update_post(client, user, subject, attribute):
    client.force_login(user)
    url = f'/subjects/{subject.pk}/attributes/'
    response = client.post(url, {
        'd1': 1,
        'd2': 'de',
    })
    assert response.status_code == 302

    subject.refresh_from_db()
    assert subject.attributes['d1'] == 1
    assert subject.attributes['d2'] == 'de'


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_delete_attributes_200(request, client, user_fixture, subject):
    """The attributes deletion view should only be accessible if you have the
    "change subject" permission."""
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = f'/subjects/{subject.pk}/attributes/delete/'
    response = client.get(url)
    assert response.status_code == 200


def test_delete_attributes_post(client, user, subject, study_types):
    """Test that the attributes are empty after "delete attributes" was performed
    in the DeleteRecruitmentDataView."""

    settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID = None
    client.force_login(user)
    url = f'/subjects/{subject.pk}/attributes/delete/'

    subject.attributes['d1'] = 1
    subject.attributes['d2'] = 'de'
    subject.study_type_disinterest.add(StudyType.objects.first())
    subject.save()
    subject.refresh_from_db()

    assert subject.attributes
    assert subject.study_type_disinterest.exists()

    client.post(url)
    subject.refresh_from_db()

    assert not subject.attributes
    assert not subject.study_type_disinterest.exists()


def test_birth_attribute_remains(client, user, subject):
    """Check that birthday attribute is retained through attribute deletion."""

    settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID = 3
    client.force_login(user)
    url = f'/subjects/{subject.pk}/attributes/delete/'

    date_of_birth = '1989-05-02'

    key = Attribute.objects.get(
        pk=settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID
    ).json_key

    subject.attributes[key] = date_of_birth
    subject.save()

    assert subject.attributes[key] == date_of_birth

    client.post(url)
    subject.refresh_from_db()

    assert subject.attributes[key] == date_of_birth
