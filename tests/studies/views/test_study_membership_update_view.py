from django.urls import reverse

import pytest
from model_mommy import mommy

from castellum.studies.models import StudyMembership
from castellum.studies.views.studies import StudyMembershipUpdateView


@pytest.fixture
def view(request_factory, prepared_user):
    request = request_factory.post(reverse("studies:member", kwargs=dict(study_pk=1, pk=1)))

    view = StudyMembershipUpdateView()
    view.request = request
    view.request.user = prepared_user
    return view


@pytest.mark.unittest
def test_get_success_url(view, prepared_study):
    view.object = mommy.prepare(StudyMembership, study=prepared_study)

    assert "/studies/{}/members/".format(prepared_study.pk) == view.get_success_url()
