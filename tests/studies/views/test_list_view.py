from model_bakery import baker

from castellum.studies.models import Study


def test_list_count_own_tab(client, study_coordinator):
    baker.make(Study, _quantity=3)

    client.force_login(study_coordinator)
    response = client.get('/studies/')

    assert response.content.count(b'class="table-list-item"') == 0


def test_list_count_all_tab(client, study_coordinator):
    baker.make(Study, _quantity=3)

    client.force_login(study_coordinator)
    response = client.get('/studies/?q=&tab=all')

    assert response.content.count(b'class="table-list-item"') == 3
