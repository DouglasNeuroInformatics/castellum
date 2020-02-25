from unittest.mock import MagicMock

from django.contrib.messages import get_messages
from django.db.models import Q

from castellum.recruitment.filter_registry import custom_filters


def test_custom_filter_is_used(client, admin, started_study):
    client.force_login(admin)

    custom_filter = MagicMock(return_value=Q())
    custom_filters['testfilter'] = custom_filter
    started_study.min_subject_count = 10
    started_study.custom_filter = 'testfilter'
    started_study.save()

    client.post('/recruitment/{}/'.format(started_study.pk))

    assert custom_filter.called

    # manual cleanup required
    del custom_filters['testfilter']


def test_error_if_not_registered(client, admin, started_study):
    client.force_login(admin)

    started_study.min_subject_count = 10
    started_study.custom_filter = 'testfilter'
    started_study.save()

    response = client.post('/recruitment/{}/'.format(started_study.pk))

    messages = list(get_messages(response.wsgi_request))
    assert str(messages[0]) == (
        'The custom filter that is set for this study does not exist.'
    )
