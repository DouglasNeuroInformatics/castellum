from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("appointments", "0006_alter_appointment_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="appointment",
            options={
                "ordering": ["start"],
                "permissions": [
                    ("view_current_appointments", "Can view current appointments")
                ],
                "verbose_name": "Appointment",
            },
        ),
    ]
