import pytest
from model_bakery import baker

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import Domain


@pytest.mark.smoketest
def test_api_attributes_view(client, user, subject, attribute_description):
    domain = baker.make(Domain)
    domain.exportable_attributes.add(attribute_description)
    pseudonym = get_pseudonym(subject, domain.key)

    user.general_domains.add(domain)

    url = f'/subjects/api/subjects/{domain.key}/{pseudonym}/attributes/'
    response = client.get(url, HTTP_AUTHORIZATION='token ' + user.token)

    assert response.status_code == 200
    data = response.json()
    assert data == {attribute_description.label: None, 'privacy_level': 0}


def test_api_attributes_view_no_user_access(client, user, subject, attribute_description):
    domain = baker.make(Domain)
    domain.exportable_attributes.add(attribute_description)
    pseudonym = get_pseudonym(subject, domain.key)

    url = f'/subjects/api/subjects/{domain.key}/{pseudonym}/attributes/'
    response = client.get(url, HTTP_AUTHORIZATION='token ' + user.token)

    assert response.status_code == 404
