from django.db import migrations


def migrate_data(apps, schema_editor):
    Appointment = apps.get_model('appointments', 'Appointment')
    Appointment.objects.exclude(participation__status=3).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('appointments', '0003_squashed_initial'),
        ('recruitment', '0039_subject_uuid_foreign_key'),
    ]

    operations = [
        migrations.RunPython(migrate_data),
    ]
