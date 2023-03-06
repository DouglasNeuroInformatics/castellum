import re

import pytest
from model_bakery import baker

from castellum.recruitment.models import SubjectFilterGroup
from castellum.studies.models import Study
from castellum.studies.models import StudyMembership


@pytest.mark.smoketest
def test_update_200(client, member, subject_filter_group):
    client.force_login(member)
    study = subject_filter_group.study
    url = f'/studies/{study.pk}/recruitmentsettings/filters/{subject_filter_group.pk}/'
    response = client.get(url)
    assert response.status_code == 200


def test_update_with_filter_200(client, member, subject_filter):
    client.force_login(member)
    group = subject_filter.group
    url = f'/studies/{group.study.pk}/recruitmentsettings/filters/{group.pk}/'
    response = client.get(url)
    assert response.status_code == 200


def test_update_other_study(client, member, subject_filter_group):
    client.force_login(member)
    other_study = baker.make(Study)
    baker.make(StudyMembership, user=member, study=other_study)
    url = '/studies/{}/recruitmentsettings/filters/{}/'.format(
        other_study.pk, subject_filter_group.pk
    )
    response = client.get(url)
    assert response.status_code == 404


def test_delete_200(client, member, subject_filter_group):
    client.force_login(member)
    study = subject_filter_group.study
    url = '/studies/{}/recruitmentsettings/filters/{}/delete/'.format(
        study.pk, subject_filter_group.pk
    )
    response = client.get(url)
    assert response.status_code == 200


def test_delete_other_study(client, member, subject_filter_group):
    client.force_login(member)
    other_study = baker.make(Study)
    baker.make(StudyMembership, user=member, study=other_study)
    url = '/studies/{}/recruitmentsettings/filters/{}/delete/'.format(
        other_study.pk, subject_filter_group.pk
    )
    response = client.get(url)
    assert response.status_code == 404


def test_advanced_filtering_200(client, member, subject_filter_group, study):
    study.advanced_filtering = True
    study.save()

    client.force_login(member)
    url = f'/studies/{study.pk}/recruitmentsettings/filters/'
    response = client.get(url)
    assert response.status_code == 200


def test_basic_filtering_302(client, member, study):
    client.force_login(member)
    url = f'/studies/{study.pk}/recruitmentsettings/filters/'
    response = client.get(url)
    assert response.status_code == 302


def test_get_when_study_has_minimal_subject_count_set_to_zero(
    client, member, subject_filter_group, study
):
    study.advanced_filtering = True
    study.save()

    client.force_login(member)
    url = f'/studies/{study.pk}/recruitmentsettings/filters/'
    response = client.get(url)
    assert response.status_code == 200

    expected = b'Weak recruitment process. Please, define the number of subjects for this study.'
    assert expected in response.content


@pytest.mark.django_db
def test_get_when_study_has_not_enough_subjects_in_filter_group(
    client, member, study
):
    client.force_login(member)

    study.min_subject_count = 100
    study.advanced_filtering = True
    study.save()

    baker.make(SubjectFilterGroup, study=study)

    url = f'/studies/{study.pk}/recruitmentsettings/filters/'
    response = client.get(url)
    assert response.status_code == 200

    expected = (
        b'For a smooth recruitment process, your institution recommends at least '
        b'10\xc3\x97 more potential than required subjects (i.e. 1000 for this study). '
        b'Current amount of potential subjects: 0'
    )
    assert expected in re.sub(rb'\s+', b' ', response.content)
