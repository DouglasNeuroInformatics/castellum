from unittest.mock import patch

from django.urls import reverse

import pytest
from model_mommy import mommy

from castellum.studies.models import StudyMembership
from castellum.studies.views.studies import StudyMembershipRemoveView


@pytest.fixture
def view(request_factory, prepared_user):
    request = request_factory.post(reverse("studies:delete-member", kwargs=dict(study_pk=1, pk=1)))

    view = StudyMembershipRemoveView()
    view.request = request
    view.request.user = prepared_user
    return view


@pytest.mark.unittest
@patch.object(StudyMembership, "delete")
@patch.object(StudyMembershipRemoveView, "get_object")
def test_remove_member(get_object, membership_delete, view, prepared_study):
    user = mommy.prepare("castellum_auth.User", pk=2)
    get_object.return_value = mommy.prepare(StudyMembership, study=prepared_study, user=user)

    response = view.delete(view.request)

    membership_delete.assert_called()
    assert_redirect(response)


@pytest.mark.unittest
@patch.object(StudyMembership, "delete")
@patch.object(StudyMembershipRemoveView, "get_object")
def test_users_cannot_remove_themselves_from_study(get_object, membership_delete,
                                                   view, prepared_study):
    get_object.return_value = mommy.prepare(StudyMembership, study=prepared_study,
                                            user=view.request.user)

    response = view.delete(view.request)

    membership_delete.assert_not_called()
    assert_bad_request(response)


def assert_redirect(response):
    assert response.status_code == 302


def assert_bad_request(response):
    assert response.status_code == 400
