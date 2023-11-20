from model_bakery import baker

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import Domain
from castellum.recruitment.models import Participation


def test_apiattributesview(
    client, conductor, study_in_execution_status, subject, attribute
):
    study = study_in_execution_status
    study.exportable_attributes.add(attribute)
    domain = baker.make(Domain, context=study)
    baker.make(
        Participation, study=study, subject=subject, status=Participation.PARTICIPATING
    )
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/attributes/'.format(
        study.pk, domain.key, pseudonym
    )
    response = client.get(url, HTTP_AUTHORIZATION=f'token {conductor.token}')

    assert response.status_code == 200
    data = response.json()
    assert data == {'Handedness': None, 'privacy_level': 0}


def test_participation_status(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    baker.make(
        Participation, study=study, subject=subject, status=Participation.NOT_CONTACTED
    )
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/attributes/'.format(
        study.pk, domain.key, pseudonym
    )
    response = client.get(url, HTTP_AUTHORIZATION=f'token {conductor.token}')

    assert response.status_code == 404


def test_privacy_level(client, conductor, study_in_execution_status, subject):
    subject.privacy_level = 2
    subject.save()

    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    baker.make(
        Participation, study=study, subject=subject, status=Participation.PARTICIPATING
    )
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/attributes/'.format(
        study.pk, domain.key, pseudonym
    )
    response = client.get(url, HTTP_AUTHORIZATION=f'token {conductor.token}')

    assert response.status_code == 403


def test_unrelated_domain(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain)
    baker.make(
        Participation, study=study, subject=subject, status=Participation.PARTICIPATING
    )
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/attributes/'.format(
        study.pk, domain.key, pseudonym
    )
    response = client.get(url, HTTP_AUTHORIZATION=f'token {conductor.token}')

    assert response.status_code == 404
