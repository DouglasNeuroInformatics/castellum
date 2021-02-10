from unittest.mock import MagicMock

from django.contrib.messages import get_messages
from django.db.models import Q

from castellum.recruitment.filter_registry import custom_filters


def test_custom_filter_is_used(client, admin, study_in_execution_status):
    client.force_login(admin)

    custom_filter = MagicMock(return_value=Q())
    custom_filters['testfilter'] = custom_filter
    study_in_execution_status.min_subject_count = 10
    study_in_execution_status.custom_filter = 'testfilter'
    study_in_execution_status.save()

    client.post(f'/recruitment/{study_in_execution_status.pk}/')

    assert custom_filter.called

    # manual cleanup required
    del custom_filters['testfilter']


def test_error_if_not_registered(client, admin, study_in_execution_status):
    client.force_login(admin)

    study_in_execution_status.min_subject_count = 10
    study_in_execution_status.custom_filter = 'testfilter'
    study_in_execution_status.save()

    response = client.post(f'/recruitment/{study_in_execution_status.pk}/')

    messages = list(get_messages(response.wsgi_request))
    assert str(messages[0]) == (
        'The custom filter that is set for this study does not exist.'
    )
