from model_mommy import mommy

from castellum.studies.models import Study


def test_list_count(client, study_coordinator):
    mommy.make(Study, _quantity=3)

    client.force_login(study_coordinator)
    response = client.get('/studies/')

    assert response.content.count(b'class="table-list-item"') == 3
