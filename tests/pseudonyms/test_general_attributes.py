from model_bakery import baker

from castellum.pseudonyms.models import Domain
from castellum.recruitment.models import Participation


def test_general_domain(client, user, conductor, study_in_execution_status, subject):
    domain = baker.make(Domain)
    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        subject=subject,
        status=Participation.INVITED,
    )

    study_in_execution_status.general_domains.add(domain)
    conductor.general_domains.add(domain)

    url = '/execution/{}/{}/pseudonyms/{}/'.format(
        study_in_execution_status.pk, participation.pk, domain.key
    )
    client.force_login(conductor)
    response = client.get(url)
    assert response.status_code == 200

    participation.delete()

    url = f'/subjects/{subject.pk}/delete/'
    client.force_login(user)
    response = client.get(url)
    assert b'This subject may still have data in general domains.' in response.content


def test_general_domain_not_in_study(
    client, conductor, study_in_execution_status, subject
):
    domain = baker.make(Domain)
    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        subject=subject,
        status=Participation.INVITED,
    )

    conductor.general_domains.add(domain)

    url = '/execution/{}/{}/pseudonyms/{}/'.format(
        study_in_execution_status.pk, participation.pk, domain.key
    )
    client.force_login(conductor)
    response = client.get(url)
    assert response.status_code == 404


def test_general_domain_not_in_user(
    client, conductor, study_in_execution_status, subject
):
    domain = baker.make(Domain)
    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        subject=subject,
        status=Participation.INVITED,
    )

    study_in_execution_status.general_domains.add(domain)

    url = '/execution/{}/{}/pseudonyms/{}/'.format(
        study_in_execution_status.pk, participation.pk, domain.key
    )
    client.force_login(conductor)
    response = client.get(url)
    assert response.status_code == 404
