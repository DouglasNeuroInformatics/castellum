import pytest
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.recruitment.models import Participation
from castellum.recruitment.templatetags.recruitment import (
    study_legal_representative_hash,
)


@pytest.mark.smoketest
def test_200(client, member, participation):
    participation.status = Participation.NOT_CONTACTED
    participation.save()

    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/update-contact/'
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
def test_legal_representative_200(client, member, participation):
    participation.status = Participation.NOT_CONTACTED
    participation.save()

    contact = participation.subject.contact
    legal_representative = baker.make(Contact)
    contact.legal_representatives.add(legal_representative)

    h = study_legal_representative_hash(
        participation.study, legal_representative.subject
    )

    client.force_login(member)
    url = (
        f'/recruitment/{participation.study.pk}'
        f'/{participation.pk}/representatives/{h}/update-contact/'
    )
    response = client.get(url)
    assert response.status_code == 200
