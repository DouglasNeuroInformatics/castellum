from model_bakery import baker

from castellum.pseudonyms.models import Domain
from castellum.recruitment.models import Participation


def test_apiexportview(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)

    url = '/execution/{}/api/domains/{}/'.format(study.pk, domain.key)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    data = response.json()
    assert len(data['participants']) == 1


def test_participation_status(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject)

    url = '/execution/{}/api/domains/{}/'.format(study.pk, domain.key)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    data = response.json()
    assert len(data['participants']) == 0


def test_privacy_level(client, conductor, study_in_execution_status, subject):
    subject.privacy_level = 2
    subject.save()

    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)

    url = '/execution/{}/api/domains/{}/'.format(study.pk, domain.key)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    data = response.json()
    assert len(data['participants']) == 0


def test_unrelated_domain(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)

    url = '/execution/{}/api/domains/{}/'.format(study.pk, domain.key)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404
