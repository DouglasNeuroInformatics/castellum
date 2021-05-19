from django.core import serializers

from model_bakery import baker

from castellum.studies.models import Study
from castellum.studies.views.studies import take_snapshot
from castellum.utils.templatetags import diff


def get_snapshot(study):
    take_snapshot(study)
    return list(serializers.deserialize('json', study.snapshot, ignorenonexistent=True))


def test_diff_class(study):
    snapshot = get_snapshot(study)
    assert diff.diff_class(snapshot, study, 'name') == 'diff-unchanged'
    study.name = 'test'
    assert diff.diff_class(snapshot, study, 'name') == 'diff-changed'
    study.name = ''
    assert diff.diff_class(snapshot, study, 'name') == 'diff-removed'

    snapshot = get_snapshot(study)
    study.name = 'test'
    assert diff.diff_class(snapshot, study, 'name') == 'diff-added'


def test_diff_get_m2m(study):
    excluded1 = baker.make(Study, name='excluded1')
    excluded2 = baker.make(Study, name='excluded2')

    study.excluded_studies.add(excluded1)
    snapshot = get_snapshot(study)

    study.excluded_studies.add(excluded2)
    items = diff.diff_get_m2m(snapshot, study, 'excluded_studies')
    items = [(value.name, cls) for value, cls in items]
    assert items == [('excluded1', 'diff-unchanged'), ('excluded2', 'diff-added')]

    study.excluded_studies.clear()
    items = diff.diff_get_m2m(snapshot, study, 'excluded_studies')
    items = [(value.name, cls) for value, cls in items]
    assert items == [('excluded1', 'diff-removed')]

    excluded1.delete()
    items = diff.diff_get_m2m(snapshot, study, 'excluded_studies')
    items = [(value.name, cls) for value, cls in items]
    assert items == []


def test_diff_get_o2m(study):
    study.studytag_set.create(name='tag1')
    study.studytag_set.create(name='tag2')
    study.studytag_set.create(name='tag3')
    snapshot = get_snapshot(study)

    study.studytag_set.filter(name='tag2').update(name='tag2-edited')
    study.studytag_set.filter(name='tag3').delete()
    study.studytag_set.create(name='tag4')
    items = diff.diff_get_o2m(snapshot, study, 'studytag_set')
    items = [(value.name, cls) for value, cls in items]
    assert items == [
        ('tag1', 'diff-unchanged'),
        ('tag2-edited', 'diff-changed'),
        ('tag4', 'diff-added'),
        ('tag3', 'diff-removed'),
    ]
