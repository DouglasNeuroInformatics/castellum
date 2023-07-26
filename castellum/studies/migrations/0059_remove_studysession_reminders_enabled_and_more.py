from django.conf import settings
from django.db import migrations, models


def migrate_data(apps, schema_editor):
    StudySession = apps.get_model('studies', 'StudySession')
    old_default = settings.CASTELLUM_APPOINTMENT_REMINDER_PERIOD.days

    for session in StudySession.objects.all():
        if session.reminders_enabled:
            session.first_reminder_days = old_default
            session.second_reminder_days = None
        else:
            session.first_reminder_days = None
            session.second_reminder_days = None
        session.save()


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0058_studylock"),
    ]

    operations = [
        migrations.AddField(
            model_name="studysession",
            name="first_reminder_days",
            field=models.PositiveIntegerField(
                blank=True, default=3, null=True, verbose_name="First reminder"
            ),
        ),
        migrations.AddField(
            model_name="studysession",
            name="second_reminder_days",
            field=models.PositiveIntegerField(
                blank=True, default=None, null=True, verbose_name="Second reminder"
            ),
        ),
        migrations.RunPython(migrate_data),
        migrations.RemoveField(
            model_name="studysession",
            name="reminders_enabled",
        ),
    ]
