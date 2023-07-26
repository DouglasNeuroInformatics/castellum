from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("appointments", "0007_alter_appointment_options"),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='reminded',
            new_name='first_reminder_sent',
        ),
        migrations.AlterField(
            model_name="appointment",
            name="first_reminder_sent",
            field=models.BooleanField(
                default=False, verbose_name="First reminder sent"
            ),
        ),
        migrations.AddField(
            model_name="appointment",
            name="second_reminder_sent",
            field=models.BooleanField(
                default=False, verbose_name="Second reminder sent"
            ),
        ),
    ]
