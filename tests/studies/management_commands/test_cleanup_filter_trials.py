from model_bakery import baker

from castellum.studies.management.commands.cleanup_filter_trials import Command
from castellum.studies.models import Study


def test_cleanup_filter_trial(study):
    baker.make(Study, is_filter_trial=True)

    cmd = Command()
    cmd.handle()

    assert not Study.objects.filter(is_filter_trial=True).exists()
    assert Study.objects.filter(pk=study.pk).exists()
    assert Study.objects.count() == 1
