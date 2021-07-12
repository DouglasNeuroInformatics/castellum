from castellum.studies.management.commands.delete_filter_previews import Command
from castellum.studies.models import Study


def test_delete_filter_preview(study):
    study.is_filter_preview = True
    study.save()

    cmd = Command()
    cmd.handle()

    assert not Study.objects.exists()
