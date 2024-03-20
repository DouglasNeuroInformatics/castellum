from model_bakery import baker

from castellum.pseudonyms.models import Domain
from castellum.pseudonyms.models import Pseudonym
from castellum.recruitment.models import Participation
from castellum.studies.models import Study


def test_single_domain(client, conductor, study):
    baker.make(Domain, context=study)

    client.force_login(conductor)
    url = f'/execution/{study.pk}/export/'
    response = client.get(url)

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/zip'


def test_no_domain(client, conductor, study):
    client.force_login(conductor)
    url = f'/execution/{study.pk}/export/'
    response = client.get(url)

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html; charset=utf-8'
    assert b'All pseudonym domains have been deleted.' in response.content


def test_multi_domain(client, conductor, study):
    baker.make(Domain, context=study)
    baker.make(Domain, context=study)

    client.force_login(conductor)
    url = f'/execution/{study.pk}/export/'
    response = client.get(url)

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html; charset=utf-8'


def test_multi_domain_given(client, conductor, study):
    baker.make(Participation, study=study, status=Participation.PARTICIPATING)
    baker.make(Domain, context=study)
    domain2 = baker.make(Domain, context=study)

    client.force_login(conductor)
    url = f'/execution/{study.pk}/export/?domain={domain2.key}'
    response = client.get(url)

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/zip'

    # use existence of pseudonym as indicator which domain was used
    assert domain2.pseudonym_set.count() == 1
    assert Pseudonym.objects.count() == 1


def test_multi_domain_given_invalid(client, conductor, study):
    baker.make(Domain, context=study)
    baker.make(Domain, context=study)

    client.force_login(conductor)
    url = f'/execution/{study.pk}/export/?domain=invalud'
    response = client.get(url)

    assert response.status_code == 404


def test_multi_domain_given_wrong_study(client, conductor, study):
    study2 = baker.make(Study)
    baker.make(Domain, context=study)
    domain2 = baker.make(Domain, context=study)

    client.force_login(conductor)
    url = f'/execution/{study2.pk}/export/?domain={domain2.key}'
    response = client.get(url)

    assert response.status_code == 404
