import datetime

from django.db import migrations

MINUTE = datetime.timedelta(seconds=60)


def migrate_data(apps, schema_editor):
    User = apps.get_model('castellum_auth', 'User')
    StudySession = apps.get_model('studies', 'StudySession')
    Experiment = apps.get_model('projects', 'Experiment')
    Session = apps.get_model('projects', 'Session')

    dummy_user, __ = User.objects.get_or_create(username='dummy')

    for session in StudySession.objects.all():
        experiment, __ = Experiment.objects.get_or_create(
            project=session.study.project, title='dummy', order=0
        )

        Session.objects.create(
            experiment=experiment,
            operator=dummy_user,
            title='Session',
            duration=session.duration * MINUTE,
            order=0,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('studies', '0008_drop_study_name'),
    ]

    operations = [
        migrations.RunPython(migrate_data),
        migrations.DeleteModel(
            name='StudySession',
        ),
    ]
