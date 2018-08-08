from freezegun import freeze_time

from castellum.recruitment.models import Participation


def test_404_page_returned_if_study_is_not_provided(client, user, attributeset):
    client.force_login(user)
    url = '/recruitment/3/{}/'.format(attributeset.pseudonym)
    response = client.get(url)
    assert response.status_code == 404


def test_200_page_returned_if_published_study_is_provided(
        client, user, published_study, attributeset):
    client.force_login(user)
    url = '/recruitment/{}/{}/'.format(published_study.pk, attributeset.pseudonym)
    response = client.get(url)
    assert response.status_code == 200


def test_404_page_returned_if_unpublished_study_is_provided(
        client, user, unpublished_study, attributeset):
    client.force_login(user)
    url = '/recruitment/{}/{}/'.format(unpublished_study.pk, attributeset.pseudonym)
    response = client.get(url)
    assert response.status_code == 404


def test_post_redirect(client, user, published_study, attributeset):
    client.force_login(user)
    url = '/recruitment/{}/{}/'.format(published_study.pk, attributeset.pseudonym)
    response = client.post(url, {'status': 2})
    assert response.status_code == 302
    assert response.url == '/recruitment/{}/'.format(published_study.pk)


@freeze_time('2018-01-01')
def test_post_updated_at(client, user, published_study, attributeset):
    client.force_login(user)
    url = '/recruitment/{}/{}/'.format(published_study.pk, attributeset.pseudonym)
    client.post(url, {'status': 2})
    participation = Participation.objects.get()
    assert participation.updated_at.strftime('%Y-%m-%d') == '2018-01-01'
