import pytest
from model_bakery import baker

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import CodingList


@pytest.mark.smoketest
def test_api_attributes_view(client, user, subject, attribute_description):
    coding_list = baker.make(CodingList)
    coding_list.exportable_attributes.add(attribute_description)
    pseudonym = get_pseudonym(subject, coding_list.key)

    user.general_coding_lists.add(coding_list)

    url = '/subjects/api/subjects/{}/{}/attributes/'.format(coding_list.key, pseudonym)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + user.token)

    assert response.status_code == 200
    data = response.json()
    assert data == {attribute_description.label: None}


def test_api_attributes_view_no_user_access(client, user, subject, attribute_description):
    coding_list = baker.make(CodingList)
    coding_list.exportable_attributes.add(attribute_description)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/subjects/api/subjects/{}/{}/attributes/'.format(coding_list.key, pseudonym)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + user.token)

    assert response.status_code == 404
