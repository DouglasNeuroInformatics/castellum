from castellum.studies.management.commands.delete_filter_trials import Command
from castellum.studies.models import Study


def test_delete_filter_trial(study):
    study.is_filter_trial = True
    study.save()

    cmd = Command()
    cmd.handle()

    assert not Study.objects.exists()
