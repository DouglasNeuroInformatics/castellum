from django.contrib.messages import get_messages

import pytest
from model_mommy import mommy

from castellum.studies.models import Study
from castellum.recruitment.models import SubjectFilterGroup


def test_update_200(client, user, subject_filter_group):
    client.force_login(user)
    study = subject_filter_group.study
    url = '/recruitment/filter/{}/{}/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_update_with_filter_200(client, user, subject_filter):
    client.force_login(user)
    group = subject_filter.group
    url = '/recruitment/filter/{}/{}/'.format(group.study.pk, group.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_update_other_study(client, user, subject_filter_group, study):
    client.force_login(user)
    url = '/recruitment/filter/{}/{}/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_delete_200(client, user, subject_filter_group):
    client.force_login(user)
    study = subject_filter_group.study
    url = '/recruitment/filter/{}/{}/delete/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_delete_other_study(client, user, subject_filter_group, study):
    client.force_login(user)
    url = '/recruitment/filter/{}/{}/delete/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_nonempty_list_200(client, user, subject_filter_group, unpublished_study):
    client.force_login(user)
    url = '/recruitment/filter/{}/'.format(unpublished_study.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_empty_list_302(client, user, unpublished_study):
    client.force_login(user)
    url = '/recruitment/filter/{}/'.format(unpublished_study.pk)
    response = client.get(url)
    assert response.status_code == 302


def test_get_when_study_has_minimal_subject_count_set_to_zero(client, user, subject_filter_group,
                                                              unpublished_study):
    client.force_login(user)
    url = '/recruitment/filter/{}/'.format(unpublished_study.pk)
    response = client.get(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'Weak recruitment process. The number of subjects is ' \
                               'not defined for this study.'


@pytest.mark.django_db
def test_get_when_study_has_not_enough_subjects_in_filter_group(client, user):
    client.force_login(user)

    unpublished_study = mommy.make(Study, published=False, min_subjects_count=100)
    unpublished_study.save()

    mommy.make(SubjectFilterGroup, study=unpublished_study)

    url = '/recruitment/filter/{}/'.format(unpublished_study.pk)
    response = client.get(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'The number of potential subjects is probably ' \
                               'not sufficient for this study.'
