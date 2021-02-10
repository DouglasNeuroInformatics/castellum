import pytest
from model_bakery import baker

from castellum.studies.models import Study
from castellum.studies.models import StudyMembership

MANAGEMENT_FORM = {
    'form-TOTAL_FORMS': 0,
    'form-INITIAL_FORMS': 0,
    'form-MIN_NUM_FORMS': 0,
    'form-MAX_NUM_FORMS': 1000,
}

STUDY_FORM = {
        'name': 'Test study',
        'contact_person': 'Mustermann',
        'principal_investigator': 'Mustermann',
        'min_subject_count': 0,
        'phone': "030123456789",
        'email': "test@example.com",
        **MANAGEMENT_FORM,
}


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_get_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/studies/create/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_redirect_to_studies_after_post(client, study_coordinator):
    client.force_login(study_coordinator)
    response = client.post('/studies/create/', STUDY_FORM)

    assert response.status_code == 302
    assert response.url == '/studies/'


@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_create_study_on_post(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    client.post('/studies/create/', STUDY_FORM)

    assert Study.objects.count() == 1
    assert Study.objects.last().name == 'Test study'


def test_duplicate_study_get(client, user):
    client.force_login(user)
    original = baker.make(Study, name="Test study", members=[user])
    response = client.get(f'/studies/create/?duplicate_pk={original.pk}')

    assert response.status_code == 200
    assert b'value="Copy Test study"' in response.content


def test_duplicate_study_404(client, user):
    client.force_login(user)
    response = client.get('/studies/create/?duplicate_pk=13')
    assert response.status_code == 404


def test_duplicate_study_post(client, user):
    client.force_login(user)
    original = baker.make(Study, recruitment_text='foo bar', members=[user])
    response = client.post(f'/studies/create/?duplicate_pk={original.pk}', STUDY_FORM)

    assert response.status_code == 302
    assert Study.objects.count() == 2
    assert Study.objects.last().recruitment_text == 'foo bar'


@pytest.mark.django_db
def test_user_who_created_study_is_study_member(client, study_coordinator):
    client.force_login(study_coordinator)
    response = client.post('/studies/create/', STUDY_FORM)

    assert response.status_code == 302
    assert StudyMembership.objects.last().study.name == 'Test study'
    assert StudyMembership.objects.last().user.username == study_coordinator.username


def test_missing_value(client, user):
    client.force_login(user)
    response = client.post('/studies/create/', {
        'name': 'Test study',
        'principal_investigator': 'Mustermann',
        'min_subject_count': 0,
        **MANAGEMENT_FORM,
    })
    assert response.status_code == 200
