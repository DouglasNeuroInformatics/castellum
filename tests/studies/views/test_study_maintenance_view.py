from datetime import date
from datetime import timedelta

import pytest
from model_bakery import baker

from castellum.pseudonyms.models import Domain
from castellum.studies.models import Study
from castellum.studies.views.studies import StudyMaintenanceView


@pytest.mark.usefixtures
@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    pytest.param('receptionist', marks=pytest.mark.xfail(strict=True)),
])
def test_study_maintenance_200(request, client, user_fixture, study):
    """
    Only people who can view studies should be able to see this view,
    because it shows a list of all studies.
    """

    this_user = request.getfixturevalue(user_fixture)
    client.force_login(this_user)
    response = client.get('/studies/maintenance/edit/')
    assert response.status_code == 200


def test_studies_start_in_edit(client, user):
    """
    A study that has been freshly created should start in "edit".
    """
    baker.make(Study, _quantity=3)

    client.force_login(user)
    response = client.get('/studies/maintenance/edit/')

    assert response.content.count(b'class="table-list-item"') == 3


def test_finished_study_in_finished(client, user, study_in_finished_status):
    """
    A finished study should be in one of the "finished-" views.
    """
    client.force_login(user)

    finished_subtabs = [
        subtab for subtab in StudyMaintenanceView.NEXT_STEPS
        if subtab.startswith('finished-')
    ]

    assert finished_subtabs, ("Couldn't find any subtabs for finished studies"
                              " in the maintenance view. Found subtabs: "
                              f"{list(StudyMaintenanceView.NEXT_STEPS)}")

    for subtab in finished_subtabs:
        response = client.get(f'/studies/maintenance/{subtab}/')
        if response.content.count(b'class="table-list-item"') == 1:
            break
    else:
        assert False


def test_each_study_in_exactly_one_view(client, user):
    """
    Every study should be visible on the maintenance view, which means that it has
    to be part of at least one tab.
    Every study should also only be visible on *at most* one tab.
    """
    client.force_login(user)

    baker.make(Study, name='Fresh Study')

    tomorrow = date.today() + timedelta(1),
    yesterday = date.today() - timedelta(1)

    baker.make(Study, status=Study.EXECUTION, name='Execution Unknown')
    baker.make(Study, status=Study.EXECUTION, sessions_end=str(tomorrow),
               name='Execution Future')
    baker.make(Study, status=Study.EXECUTION, sessions_end=str(yesterday),
               name='Execution Past')

    baker.make(Study, status=Study.FINISHED, name='Finished Domains')
    domain = baker.make(Domain)
    baker.make(Study, status=Study.FINISHED, name='Finished Anon').domains.add(domain)

    name_appearances = {this_study.name: [] for this_study in Study.objects.all()}

    for subtab in StudyMaintenanceView.NEXT_STEPS:
        response = client.get(f'/studies/maintenance/{subtab}/')
        for study_in_response in response.context['study_list']:
            name_appearances[study_in_response.name].append(subtab)

    no_appearances = {
        name: appearances for name, appearances in name_appearances.items()
        if len(appearances) == 0
    }
    multi_appearances = {
        name: appearances for name, appearances in name_appearances.items()
        if len(appearances) > 1
    }

    assert not no_appearances, (f'Studies could not be found in any tab of the'
                                f' maintenance view: {multi_appearances}')
    assert not multi_appearances, (f'Found appearances in multiple maintenance tabs for'
                                   f' {len(no_appearances)} studies: {no_appearances}')
