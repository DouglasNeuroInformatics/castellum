from datetime import date
from datetime import timedelta

import pytest
from model_bakery import baker

from castellum.pseudonyms.models import Domain
from castellum.studies.models import Study
from castellum.studies.views.studies import StudyMaintenanceView


def assert_subtab_for_study(study, client, expected_sub_tab):
    """Helper function that checks if a study is in exactly one sub-tab of the
    Study Maintenance View, and then returns it."""
    appearances = []

    for sub_tab in StudyMaintenanceView.NEXT_STEPS:
        response = client.get(f'/studies/maintenance/{sub_tab}/')
        if study in response.context['study_list']:
            appearances.append(sub_tab)

    assert appearances, (
        f'Study {study} was found in none of the subtabs of the StudyMaintenanceView.'
    )
    assert len(appearances) < 2, (
        f'Study {study} was found in multiple subtabs'
        f' of the StudyMaintenanceView: {appearances}.'
    )
    assert appearances[0] == expected_sub_tab, (
        f'Study {study} was expected in {expected_sub_tab} subtab of the'
        f' StudyMaintenanceView but was found in {appearances[0]} subtab instead.'
    )


@pytest.mark.usefixtures
@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'receptionist',
    pytest.param(None, marks=pytest.mark.xfail(strict=True)),
])
def test_study_maintenance_login_required(request, client, user_fixture, study):
    """
    Only people who can view studies should be able to see this view,
    because it shows a list of all studies.
    """

    if user_fixture:
        this_user = request.getfixturevalue(user_fixture)
        client.force_login(this_user)
    response = client.get('/studies/maintenance/edit/')
    assert response.status_code == 200


def test_empty_study_in_edit(client, user):
    """
    A study that has been freshly created should start in the "edit" tab.
    """
    client.force_login(user)

    study = baker.make(Study)

    assert_subtab_for_study(study, client, 'edit')


def test_study_without_execution_date_in_execution_unknown(client, user):
    """
    An empty study in Execution status should be in the "execution-unknown" subtab.
    """
    client.force_login(user)

    study = baker.make(Study, status=Study.EXECUTION, name='Execution Unknown')

    assert_subtab_for_study(study, client, 'execution-unknown')


def test_study_with_future_exuction_date_in_excution_future(client, user):
    """
    An empty study in Execution status with a future sessions_end should be in the
    "execution-future" subtab.
    """
    client.force_login(user)

    tomorrow = date.today() + timedelta(1)
    study = baker.make(
        Study,
        status=Study.EXECUTION,
        sessions_end=tomorrow.strftime('%Y-%m-%d'),
        name='Execution Future'
    )

    assert_subtab_for_study(study, client, 'execution-future')


def test_study_with_past_exuction_date_in_excution_past(client, user):
    """
    An empty study in Execution status with a past sessions_end should be in the
    "execution-past" subtab.
    """
    client.force_login(user)

    yesterday = date.today() - timedelta(1)
    study = baker.make(
        Study,
        status=Study.EXECUTION,
        sessions_end=yesterday.strftime('%Y-%m-%d'),
        name='Execution Future'
    )

    assert_subtab_for_study(study, client, 'execution-past')


def test_finished_study_without_domains_in_finished_anon(client, user):
    """
    An empty study in Finished status should be in the finished-anon subtab.
    """
    client.force_login(user)

    study = baker.make(Study, status=Study.FINISHED, name='Finished & No Domains')

    assert_subtab_for_study(study, client, 'finished-anon')


def test_finished_study_with_domains_in_finished_domains(client, user):
    """
    A study in Finished status that has an associated domain should be in the finished-domains subtab.
    """
    client.force_login(user)

    study = baker.make(Study, status=Study.FINISHED, name='Finished With Domains')
    domain = baker.make(Domain)
    study.domains.add(domain)
    study.save()

    assert_subtab_for_study(study, client, 'finished-domains')
