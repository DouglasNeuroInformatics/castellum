import pytest

from castellum.recruitment.models import Participation
from castellum.studies.models import Study


@pytest.mark.smoketest
def test_200(client, member, participation):
    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/exclude/'
    response = client.get(url)
    assert response.status_code == 200


def test_404_if_study_in_edit_status(client, member, participation):
    participation.study.status = Study.EDIT
    participation.study.save()

    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/exclude/'
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.freeze_time('2018-01-01')
def test_post_updated_at(client, member, participation):
    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/exclude/'
    client.post(url)
    participation = Participation.objects.get()
    assert participation.updated_at.strftime('%Y-%m-%d') == '2018-01-01'


@pytest.mark.freeze_time('2018-01-01')
def test_ignore_privacy_level(client, member, participation):
    client.force_login(member)

    participation.subject.privacy_level = 2
    participation.subject.save()

    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    response = client.post(url)
    assert response.status_code == 403

    url = f'/recruitment/{participation.study.pk}/{participation.pk}/exclude/'
    response = client.post(url)
    assert response.status_code == 302
