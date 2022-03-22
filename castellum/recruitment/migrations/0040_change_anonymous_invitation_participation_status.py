from django.db import migrations

STUDY_FINISHED = 2
PARTICIPATION_AWAITING_RESPONSE = 5


def migrate_data(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')

    for study in Study.objects.filter(is_anonymous_invitation=True):
        if study.status == STUDY_FINISHED:
            study.participation_set.all().delete()
        else:
            study.participation_set.all().update(status=PARTICIPATION_AWAITING_RESPONSE)


class Migration(migrations.Migration):
    dependencies = [
        ('recruitment', '0039_subject_uuid_foreign_key'),
        ('studies', '0046_rename_study_is_onetime_invitation'),
    ]

    operations = [
        migrations.RunPython(migrate_data),
    ]
