import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.pseudonyms.models import Domain
from castellum.studies.models import Study
from castellum.studies.views.studies import StudyMaintenanceView


def assert_subtab_for_study(study, client, expected_sub_tab):
    appearances = []
    for sub_tab in StudyMaintenanceView.NEXT_STEPS:
        response = client.get(f'/studies/maintenance/{sub_tab}/')
        if study in response.context['study_list']:
            appearances.append(sub_tab)

    assert appearances, (
        f'Study {study} was found in none of the subtabs of the StudyMaintenanceView.'
    )
    assert len(appearances) < 2, (
        f'Study {study} was found in multiple subtabs '
        f'of the StudyMaintenanceView: {appearances}.'
    )
    assert appearances[0] == expected_sub_tab, (
        f'Study {study} was expected in {expected_sub_tab} subtab of the '
        f'StudyMaintenanceView but was found in {appearances[0]} subtab instead.'
    )


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'receptionist',
    pytest.param(None, marks=pytest.mark.xfail(strict=True)),
])
def test_login_required(request, client, user_fixture, study):
    if user_fixture:
        this_user = request.getfixturevalue(user_fixture)
        client.force_login(this_user)
    response = client.get('/studies/maintenance/edit/')
    assert response.status_code == 200


def test_edit(client, user):
    client.force_login(user)
    study = baker.make(Study)
    assert_subtab_for_study(study, client, 'edit')


def test_execution_unknown(client, user):
    client.force_login(user)
    study = baker.make(Study, status=Study.EXECUTION)
    assert_subtab_for_study(study, client, 'execution-unknown')


@freeze_time('2024-01-02')
def test_excution_future(client, user):
    client.force_login(user)
    study = baker.make(Study, status=Study.EXECUTION, sessions_end='2024-01-03')
    assert_subtab_for_study(study, client, 'execution-future')


@freeze_time('2024-01-02')
def test_excution_past(client, user):
    client.force_login(user)
    study = baker.make(Study, status=Study.EXECUTION, sessions_end='2024-01-01')
    assert_subtab_for_study(study, client, 'execution-past')


def test_finished_domains_unknown(client, user):
    client.force_login(user)
    study = baker.make(Study, status=Study.FINISHED)
    study.domains.add(baker.make(Domain))
    assert_subtab_for_study(study, client, 'finished-domains-unknown')


@freeze_time('2024-01-02')
def test_finished_domains_future(client, user):
    client.force_login(user)
    study = baker.make(
        Study, status=Study.FINISHED, pseudonyms_delete_date='2024-01-03'
    )
    study.domains.add(baker.make(Domain))
    assert_subtab_for_study(study, client, 'finished-domains-future')


@freeze_time('2024-01-02')
def test_finished_domains_past(client, user):
    client.force_login(user)
    study = baker.make(
        Study, status=Study.FINISHED, pseudonyms_delete_date='2024-01-01'
    )
    study.domains.add(baker.make(Domain))
    assert_subtab_for_study(study, client, 'finished-domains-past')


def test_finished_anon(client, user):
    client.force_login(user)
    study = baker.make(Study, status=Study.FINISHED)
    assert_subtab_for_study(study, client, 'finished-anon')
