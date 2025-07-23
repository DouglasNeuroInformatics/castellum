import pytest

from castellum.studies.models import StudyGroup
from castellum.studies.models import StudyMembership


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('study_conductor', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_officer', marks=pytest.mark.xfail(strict=True)),
])
def test_relation_create(request, client, user_fixture, invited):
    user = request.getfixturevalue(user_fixture)
    membership = StudyMembership.objects.create(user=user, study=invited.study)
    membership.groups.add(StudyGroup.objects.get(name='Conductor'))
    client.force_login(user)

    url = f'/execution/{invited.study.pk}/{invited.pk}/relations/create/'
    response = client.get(url)
    assert response.status_code == 200
