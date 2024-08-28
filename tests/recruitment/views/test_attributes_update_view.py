from castellum.recruitment.models import Participation


def test_200(client, member, participation):
    participation.status = Participation.NOT_CONTACTED
    participation.save()

    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/update-attributes/'
    response = client.get(url)
    assert response.status_code == 200
