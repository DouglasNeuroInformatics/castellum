from django.urls import reverse

import pytest

from castellum.studies.views.studies import StudyExclusionCriteriaView


@pytest.fixture
def view(rf, prepared_user):
    request = rf.post(reverse("studies:exclusioncriteria", kwargs=dict(pk=1)))

    view = StudyExclusionCriteriaView()
    view.request = request
    view.request.user = prepared_user
    return view


@pytest.mark.unittest
def test_get_success_url(view, prepared_study):
    view.object = prepared_study

    actual = "/studies/{}/recruitmentsettings/exclusioncriteria/".format(prepared_study.pk)
    assert actual == view.get_success_url()


def test_200(client, member, study):
    client.force_login(member)
    response = client.get('/studies/{}/recruitmentsettings/exclusioncriteria/'.format(study.pk))
    assert response.status_code == 200
