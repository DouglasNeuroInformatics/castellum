import pytest

from castellum.studies.models import Study, StudyMembership


@pytest.mark.django_db
def test_redirect_to_studies_after_post(client, study_coordinator):

    client.force_login(study_coordinator)
    response = client.post('/studies/create/', {'name': 'Test study',
                                                'contact_person': 'Mustermann'})

    assert response.status_code == 302
    assert response.url == '/studies/'


@pytest.mark.django_db
def test_create_study_on_post(client, study_coordinator):

    client.force_login(study_coordinator)
    client.post('/studies/create/', {'name': 'Test study', 'contact_person': 'Mustermann'})

    assert Study.objects.all().count() == 1
    assert Study.objects.last().name == 'Test study'


@pytest.mark.django_db
def test_user_who_created_study_is_study_member(client, study_coordinator):

    client.force_login(study_coordinator)
    response = client.post('/studies/create/', {'name': 'Test study',
                                                'contact_person': 'Mustermann'})

    assert response.status_code == 302
    assert StudyMembership.objects.last().study.name == 'Test study'
    assert StudyMembership.objects.last().user.username == study_coordinator.username
