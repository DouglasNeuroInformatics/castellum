from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')
    StudySession = apps.get_model('studies', 'StudySession')

    for study in Study.objects.all():
        if not study.study_type.exists():
            continue
        try:
            session = study.studysession_set.first()
        except StudySession.DoesNotExist:
            session = study.studysession_set.create(name='session', duration=0)
        session.type.set(study.study_type.all())


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0008_study_type_rm_3rd_party')
    ]

    operations = [
        migrations.AddField(
            model_name='studysession',
            name='type',
            field=models.ManyToManyField(blank=True, to='studies.StudyType', verbose_name='Type'),
        ),
        migrations.RunPython(migrate_data),
        migrations.RemoveField(
            model_name='study',
            name='study_type',
        ),
    ]
