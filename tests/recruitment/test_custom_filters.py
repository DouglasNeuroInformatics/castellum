from unittest.mock import MagicMock

from django.db.models import Q

from castellum.recruitment.filter_registry import custom_filters


def test_custom_filter_is_used(client, admin, published_study):
    client.force_login(admin)

    custom_filter = MagicMock(return_value=Q())
    custom_filters['testfilter'] = custom_filter
    published_study.min_subjects_count = 10
    published_study.custom_filter = 'testfilter'
    published_study.save()

    client.post('/recruitment/{}/'.format(published_study.pk))

    assert custom_filter.called

    # manual cleanup required
    del custom_filters['testfilter']
