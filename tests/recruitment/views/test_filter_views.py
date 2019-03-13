from django.contrib.messages import get_messages

import pytest
from model_mommy import mommy

from castellum.recruitment.models import SubjectFilterGroup


def test_update_200(client, member, subject_filter_group):
    client.force_login(member)
    study = subject_filter_group.study
    url = '/recruitment/filter/{}/{}/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_update_with_filter_200(client, member, subject_filter):
    client.force_login(member)
    group = subject_filter.group
    url = '/recruitment/filter/{}/{}/'.format(group.study.pk, group.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_update_other_study(client, member, subject_filter_group, study):
    client.force_login(member)
    url = '/recruitment/filter/{}/{}/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_update_403_privacy_level(client, member, subject_filter):
    subject_filter.description.privacy_level_read = 2
    subject_filter.description.privacy_level_write = 2
    subject_filter.description.save()

    client.force_login(member)
    group = subject_filter.group
    url = '/recruitment/filter/{}/{}/'.format(group.study.pk, group.pk)
    response = client.get(url)
    assert response.status_code == 403


def test_delete_200(client, member, subject_filter_group):
    client.force_login(member)
    study = subject_filter_group.study
    url = '/recruitment/filter/{}/{}/delete/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_delete_other_study(client, member, subject_filter_group, study):
    client.force_login(member)
    url = '/recruitment/filter/{}/{}/delete/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_advanced_filtering_200(client, member, subject_filter_group, unpublished_study):
    unpublished_study.advanced_filtering = True
    unpublished_study.save()

    client.force_login(member)
    url = '/recruitment/filter/{}/'.format(unpublished_study.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_basic_filtering_302(client, member, unpublished_study):
    client.force_login(member)
    url = '/recruitment/filter/{}/'.format(unpublished_study.pk)
    response = client.get(url)
    assert response.status_code == 302


def test_get_when_study_has_minimal_subject_count_set_to_zero(client, member, subject_filter_group,
                                                              unpublished_study):
    unpublished_study.advanced_filtering = True
    unpublished_study.save()

    client.force_login(member)
    url = '/recruitment/filter/{}/'.format(unpublished_study.pk)
    response = client.get(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'Weak recruitment process. Please, define the number of subjects ' \
                               'for this study.'


@pytest.mark.django_db
def test_get_when_study_has_not_enough_subjects_in_filter_group(client, member, unpublished_study):
    client.force_login(member)

    unpublished_study.min_subjects_count = 100
    unpublished_study.advanced_filtering = True
    unpublished_study.save()

    mommy.make(SubjectFilterGroup, study=unpublished_study)

    url = '/recruitment/filter/{}/'.format(unpublished_study.pk)
    response = client.get(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == (
        'For a smooth recruitment process, your institution recommends at least '
        '10x more potential than required subjects (i.e. 1000 for this study). '
        'Current amount of potential subjects: 0'
    )
