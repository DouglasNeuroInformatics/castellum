from django.utils import timezone

from freezegun import freeze_time
from model_bakery import baker

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import Domain
from castellum.recruitment.models import Participation
from castellum.studies.models import Study


def test_apiresolveview(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    target_domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)
    target_pseudonym = get_pseudonym(subject, target_domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    assert response.json() == {'pseudonym': target_pseudonym}


def test_token_required(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    target_domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    response = client.get(url)  # no token

    assert response.status_code == 403


def test_user_expired(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    target_domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    with freeze_time('2000-01-01'):
        conductor.expiration_date = timezone.now()
        conductor.save()

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    with freeze_time('2000-01-02'):
        response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 403


def test_token_required_logged_in(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    target_domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    client.force_login(conductor)
    response = client.get(url)  # no token

    assert response.status_code == 403


def test_permission_required(client, recruiter, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    target_domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + recruiter.token)

    assert response.status_code == 403


def test_privacy_level(client, conductor, study_in_execution_status, subject):
    subject.privacy_level = 2
    subject.save()

    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    target_domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 403


def test_study_status(client, conductor, study, subject):
    domain = baker.make(Domain, context=study)
    target_domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_participation_status(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    target_domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.NOT_CONTACTED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_source_domain_wrong_study(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status

    other_study = baker.make(Study)
    domain = baker.make(Domain, context=other_study)

    target_domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_source_domain_general(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status

    domain = baker.make(Domain)
    study.general_domains.add(domain)
    conductor.general_domains.add(domain)

    target_domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_target_domain_other_study(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)

    other_study = baker.make(Study)
    target_domain = baker.make(Domain, context=other_study)

    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_target_domain_general(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)

    target_domain = baker.make(Domain)
    study.general_domains.add(target_domain)
    conductor.general_domains.add(target_domain)

    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)
    target_pseudonym = get_pseudonym(subject, target_domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    assert response.json() == {'pseudonym': target_pseudonym}


def test_target_domain_general_bad_user(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)

    target_domain = baker.make(Domain)
    study.general_domains.add(target_domain)

    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_source_domain_general_bad_study(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)

    target_domain = baker.make(Domain)
    conductor.general_domains.add(target_domain)

    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym, target_domain.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_normalize_pseudonym(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    domain = baker.make(Domain, context=study)
    target_domain = baker.make(Domain, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, domain.key)
    target_pseudonym = get_pseudonym(subject, target_domain.key)

    url = '/execution/api/studies/{}/domains/{}/{}/{}/'.format(
        study.pk, domain.key, pseudonym.lower(), target_domain.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    assert response.json() == {'pseudonym': target_pseudonym}
