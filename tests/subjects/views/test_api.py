import pytest
from model_bakery import baker

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import Domain


@pytest.mark.smoketest
def test_api_study_detail_view(client, user, subject, attribute_description):
    domain = baker.make(Domain)
    domain.exportable_attributes.add(attribute_description)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/subjects/api/subjects/{}/{}/attributes/'.format(domain.key, pseudonym)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + user.token)

    assert response.status_code == 200
    data = response.json()
    assert data == {attribute_description.label: None}
