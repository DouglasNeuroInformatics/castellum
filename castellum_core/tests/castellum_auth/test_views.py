import pytest


@pytest.mark.parametrize('language', ('de', 'en'))
def test_set_language(client, user, language):
    client.force_login(user)
    client.post('/i18n/', {'language': language})
    user.refresh_from_db()
    assert user.language == language


def test_set_language_next(client):
    response = client.post('/i18n/', {'next': '/asd/'})
    assert response.url == '/asd/'
