from django.urls import reverse

import pytest
from model_mommy import mommy

from castellum.studies.models import StudyMembership
from castellum.studies.views.studies import StudyMembershipUpdateView


@pytest.fixture
def view(rf, prepared_user):
    request = rf.post(reverse("studies:member", kwargs=dict(study_pk=1, pk=1)))

    view = StudyMembershipUpdateView()
    view.request = request
    view.request.user = prepared_user
    return view


@pytest.mark.unittest
def test_get_success_url(view, prepared_study):
    view.object = mommy.prepare(StudyMembership, study=prepared_study)

    assert "/studies/{}/members/".format(prepared_study.pk) == view.get_success_url()


def test_200(client, member, study):
    client.force_login(member)
    membership = StudyMembership.objects.get(study=study, user=member)
    response = client.get('/studies/{}/members/{}/'.format(study.pk, membership.pk))
    assert response.status_code == 200
