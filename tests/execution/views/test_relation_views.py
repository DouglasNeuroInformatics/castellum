import pytest
from model_bakery import baker

from castellum.recruitment.models import Relation
from castellum.recruitment.models import RelationType
from castellum.studies.models import StudyGroup
from castellum.studies.models import StudyMembership


def make_relation_type():
    type = RelationType.objects.create(key='parent', reverse_key='child')
    type.translations.create(
        language_code='en', label='parent', reverse_label='child'
    )
    return type


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


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('study_conductor', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_officer', marks=pytest.mark.xfail(strict=True)),
])
def test_relation_delete(request, client, user_fixture, invited):
    user = request.getfixturevalue(user_fixture)
    membership = StudyMembership.objects.create(user=user, study=invited.study)
    membership.groups.add(StudyGroup.objects.get(name='Conductor'))
    client.force_login(user)

    relation = baker.make(Relation, subject=invited.subject, type=make_relation_type())

    url = f'/execution/{invited.study.pk}/{invited.pk}/relations/{relation.pk}/delete/'
    response = client.get(url)
    assert response.status_code == 200


def test_relation_delete_subject_privacy_level(request, client, member, invited):
    client.force_login(member)

    relation = baker.make(Relation, subject=invited.subject, type=make_relation_type())
    relation.subject.privacy_level = 2
    relation.subject.save()

    url = f'/execution/{invited.study.pk}/{invited.pk}/relations/{relation.pk}/delete/'
    response = client.get(url)
    assert response.status_code == 403


def test_relation_delete_other_privacy_level(request, client, member, invited):
    client.force_login(member)

    relation = baker.make(Relation, subject=invited.subject, type=make_relation_type())
    relation.other.privacy_level = 2
    relation.other.save()

    url = f'/execution/{invited.study.pk}/{invited.pk}/relations/{relation.pk}/delete/'
    response = client.get(url)
    assert response.status_code == 403


def test_relation_delete_inconsistent_pariticipation(request, client, member, invited):
    client.force_login(member)

    relation = baker.make(Relation, type=make_relation_type())

    url = f'/execution/{invited.study.pk}/{invited.pk}/relations/{relation.pk}/delete/'
    response = client.get(url)
    assert response.status_code == 404
