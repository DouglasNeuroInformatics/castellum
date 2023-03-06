from lxml.html import fromstring

from castellum.studies.models import StudyMembership


def test_filter_button_no_filters(client, study, study_coordinator):
    StudyMembership.objects.create(study=study, user=study_coordinator)

    client.force_login(study_coordinator)
    response = client.get(f'/studies/{study.pk}/recruitmentsettings/')

    html = fromstring(response.content)
    matches = html.xpath('///*[contains(@class, "list-group-item")][contains(., "Filters")]')
    assert matches
    assert 'disabled' not in matches[-1].attrib


def test_filter_button_allowed_filters(client, study, subject_filter, study_coordinator):
    StudyMembership.objects.create(study=study, user=study_coordinator)
    subject_filter.group.study = study
    subject_filter.group.save()

    client.force_login(study_coordinator)
    response = client.get(f'/studies/{study.pk}/recruitmentsettings/')

    html = fromstring(response.content)
    matches = html.xpath('///*[contains(@class, "list-group-item")][contains(., "Filters")]')
    assert matches
    assert 'disabled' not in matches[-1].attrib
