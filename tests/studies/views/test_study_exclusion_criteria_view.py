from django.urls import reverse

import pytest

from castellum.studies.views.studies import StudyExclusionCriteriaView


@pytest.fixture
def view(request_factory, prepared_user):
    request = request_factory.post(reverse("studies:exclusioncriteria", kwargs=dict(pk=1)))

    view = StudyExclusionCriteriaView()
    view.request = request
    view.request.user = prepared_user
    return view


@pytest.mark.unittest
def test_get_success_url(view, prepared_study):
    view.object = prepared_study

    assert "/studies/{}/recruitmentsettings/".format(prepared_study.pk) == view.get_success_url()
