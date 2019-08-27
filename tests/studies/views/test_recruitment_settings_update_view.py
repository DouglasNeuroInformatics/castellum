from django.urls import reverse

import pytest

from castellum.studies.views.studies import StudyRecruitmentSettingsUpdateView


@pytest.fixture
def view(rf, prepared_user):
    request = rf.post(reverse("studies:recruitmentsettings-update", kwargs=dict(pk=1)))

    view = StudyRecruitmentSettingsUpdateView()
    view.request = request
    view.request.user = prepared_user
    return view


@pytest.mark.unittest
def test_get_success_url(view, prepared_study):
    view.object = prepared_study

    actual = "/studies/{}/recruitmentsettings/update/".format(prepared_study.pk)
    assert actual == view.get_success_url()


def test_200(client, member, study):
    client.force_login(member)
    response = client.get('/studies/{}/recruitmentsettings/update/'.format(study.pk))
    assert response.status_code == 200
