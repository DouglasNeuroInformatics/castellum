from django.db import migrations, models

EDIT = 0
EXECUTION = 1
FINISHED = 2


def migrate_value(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    for study in Study.objects.all():
        study.finished = study.status == FINISHED
        if study.finished:
            study.started = study.previous_status == EXECUTION
        else:
            study.started = study.status == EXECUTION
        study.save()


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0005_study_to_be_deleted_notified'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='finished',
            field=models.BooleanField(default=False, verbose_name='Finished'),
        ),
        migrations.AddField(
            model_name='study',
            name='started',
            field=models.BooleanField(default=False, verbose_name='Started'),
        ),
        migrations.RunPython(migrate_value),
        migrations.RemoveField(
            model_name='study',
            name='previous_status',
        ),
        migrations.RemoveField(
            model_name='study',
            name='status',
        ),
    ]
