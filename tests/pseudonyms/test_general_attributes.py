from model_bakery import baker

from castellum.pseudonyms.models import Domain
from castellum.recruitment.models import Participation


def test_general_domain(client, user, conductor, study, subject):
    domain = baker.make(Domain)
    participation = baker.make(
        Participation,
        study=study,
        subject=subject,
        status=Participation.PARTICIPATING,
    )

    study.general_domains.add(domain)
    conductor.general_domains.add(domain)

    url = f'/execution/{study.pk}/{participation.pk}/pseudonyms/{domain.key}/'
    client.force_login(conductor)
    response = client.get(url)
    assert response.status_code == 200

    participation.delete()

    url = f'/subjects/{subject.pk}/delete/'
    client.force_login(user)
    response = client.get(url)
    expected = b'This subject may still have data from general pseudonym lists.'
    assert expected in response.content


def test_general_domain_not_in_study(client, conductor, study, subject):
    domain = baker.make(Domain)
    participation = baker.make(
        Participation,
        study=study,
        subject=subject,
        status=Participation.PARTICIPATING,
    )

    conductor.general_domains.add(domain)

    url = f'/execution/{study.pk}/{participation.pk}/pseudonyms/{domain.key}/'
    client.force_login(conductor)
    response = client.get(url)
    assert response.status_code == 404


def test_general_domain_not_in_user(client, conductor, study, subject):
    domain = baker.make(Domain)
    participation = baker.make(
        Participation,
        study=study,
        subject=subject,
        status=Participation.PARTICIPATING,
    )

    study.general_domains.add(domain)

    url = f'/execution/{study.pk}/{participation.pk}/pseudonyms/{domain.key}/'
    client.force_login(conductor)
    response = client.get(url)
    assert response.status_code == 404
