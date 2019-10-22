import re

import pytest
from model_mommy import mommy

from castellum.recruitment.models import SubjectFilterGroup


def test_update_200(client, member, subject_filter_group):
    client.force_login(member)
    study = subject_filter_group.study
    url = '/studies/{}/recruitmentsettings/filters/{}/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_update_with_filter_200(client, member, subject_filter):
    client.force_login(member)
    group = subject_filter.group
    url = '/studies/{}/recruitmentsettings/filters/{}/'.format(group.study.pk, group.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_update_other_study(client, member, subject_filter_group, study):
    client.force_login(member)
    url = '/studies/{}/recruitmentsettings/filters/{}/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_update_403_privacy_level(client, member, subject_filter):
    subject_filter.description.privacy_level_read = 2
    subject_filter.description.privacy_level_write = 2
    subject_filter.description.save()

    client.force_login(member)
    group = subject_filter.group
    url = '/studies/{}/recruitmentsettings/filters/{}/'.format(group.study.pk, group.pk)
    response = client.get(url)
    assert response.status_code == 403


def test_delete_200(client, member, subject_filter_group):
    client.force_login(member)
    study = subject_filter_group.study
    url = '/studies/{}/recruitmentsettings/filters/{}/delete/'.format(
        study.pk, subject_filter_group.pk
    )
    response = client.get(url)
    assert response.status_code == 200


def test_delete_other_study(client, member, subject_filter_group, study):
    client.force_login(member)
    url = '/studies/{}/recruitmentsettings/filters/{}/delete/'.format(
        study.pk, subject_filter_group.pk
    )
    response = client.get(url)
    assert response.status_code == 404


def test_advanced_filtering_200(client, member, subject_filter_group,
                                study_in_edit_mode):
    study_in_edit_mode.advanced_filtering = True
    study_in_edit_mode.save()

    client.force_login(member)
    url = '/studies/{}/recruitmentsettings/filters/'.format(study_in_edit_mode.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_basic_filtering_302(client, member, study_in_edit_mode):
    client.force_login(member)
    url = '/studies/{}/recruitmentsettings/filters/'.format(study_in_edit_mode.pk)
    response = client.get(url)
    assert response.status_code == 302


def test_get_when_study_has_minimal_subject_count_set_to_zero(client, member, subject_filter_group,
                                                              study_in_edit_mode):
    study_in_edit_mode.advanced_filtering = True
    study_in_edit_mode.save()

    client.force_login(member)
    url = '/studies/{}/recruitmentsettings/filters/'.format(study_in_edit_mode.pk)
    response = client.get(url)
    assert response.status_code == 200

    expected = b'Weak recruitment process. Please, define the number of subjects for this study.'
    assert expected in response.content


@pytest.mark.django_db
def test_get_when_study_has_not_enough_subjects_in_filter_group(client, member,
                                                                study_in_edit_mode):
    client.force_login(member)

    study_in_edit_mode.min_subject_count = 100
    study_in_edit_mode.advanced_filtering = True
    study_in_edit_mode.save()

    mommy.make(SubjectFilterGroup, study=study_in_edit_mode)

    url = '/studies/{}/recruitmentsettings/filters/'.format(study_in_edit_mode.pk)
    response = client.get(url)
    assert response.status_code == 200

    expected = (
        b'For a smooth recruitment process, your institution recommends at least '
        b'10\xc3\x97 more potential than required subjects (i.e. 1000 for this study). '
        b'Current amount of potential subjects: 0'
    )
    assert expected in re.sub(rb'\s+', b' ', response.content)
