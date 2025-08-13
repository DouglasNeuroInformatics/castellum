import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ('appointments', '0002_squashed_appointment_participation'),
        ('appointments', '0003_squashed_initial'),
        ('appointments', '0004_rm_appointments_not_participating'),
        ('appointments', '0005_appointment_assigned_conductors'),
        ('appointments', '0006_alter_appointment_options'),
        ('appointments', '0007_alter_appointment_options'),
        ('appointments', '0008_remove_appointment_reminded_and_more'),
        ('appointments', '0009_alter_appointment_id'),
    ]

    dependencies = [
        ('studies', '0001_squashed_0066_study_recruitment_active'),
        ('recruitment', '0001_squashed_0021_initial'),
        ('appointments', '0001_squashed_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='assigned_conductors',
            field=models.ManyToManyField(blank=True, related_name='+', to='studies.studymembership', verbose_name='Assigned conductors'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='participation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruitment.participation', verbose_name='Participation'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studies.studysession', verbose_name='Session'),
        ),
        migrations.AlterUniqueTogether(
            name='appointment',
            unique_together={('session', 'participation')},
        ),
    ]
