from django.urls import reverse


URL = reverse('contacts:search')


def test_status_code_200(client, authenticated_user):
    response = client.get(URL)
    assert 200 == response.status_code
