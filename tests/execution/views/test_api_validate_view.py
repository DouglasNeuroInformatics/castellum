from model_bakery import baker
from castellum.subjects.models import PrivacyLevelLabel

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import Domain
from castellum.recruitment.models import Participation


def test_apivalidateview(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/'.format(study.pk, domain.key, pseudonym)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    assert response.json() == {'pseudonym': pseudonym}


def test_normalize_pseudonym(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/'.format(study.pk, domain.key, pseudonym.lower())
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    assert response.json() == {'pseudonym': pseudonym}


def test_unrelated_domain(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/'.format(study.pk, domain.key, pseudonym)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_ignore_privacylevel(client, conductor, study_in_execution_status, subject):
    subject.privacy_level_label = baker.make(PrivacyLevelLabel, value=2)
    subject.save()

    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/'.format(study.pk, domain.key, pseudonym)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    assert response.json() == {'pseudonym': pseudonym}
