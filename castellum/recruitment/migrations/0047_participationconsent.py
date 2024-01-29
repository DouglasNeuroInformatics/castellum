import castellum.recruitment.models.participations
import castellum.utils.fields
from django.db import migrations, models
import django.db.models.deletion


def migrate_data(apps, schema_editor):
    Participation = apps.get_model('recruitment', 'Participation')
    ParticipationConsent = apps.get_model('recruitment', 'ParticipationConsent')

    ParticipationConsent.objects.bulk_create([
        ParticipationConsent(participation=participation, file=participation.consent)
        for participation in Participation.objects.exclude(consent='')
    ])


class Migration(migrations.Migration):
    dependencies = [
        ("recruitment", "0046_remove_participation_dropped_out"),
    ]

    operations = [
        migrations.CreateModel(
            name="ParticipationConsent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(blank=True, max_length=64, verbose_name="Name"),
                ),
                (
                    "file",
                    castellum.utils.fields.RestrictedFileField(
                        upload_to=castellum.recruitment.models.participations.consent_upload_to,
                        verbose_name="File",
                    ),
                ),
                (
                    "participation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="recruitment.participation",
                    ),
                ),
            ],
            options={
                "ordering": ["pk"],
                "verbose_name": "Participation consent",
                "verbose_name_plural": "Participation consents",
            },
        ),
        migrations.RunPython(migrate_data),
        migrations.RemoveField(
            model_name="participation",
            name="consent",
        ),
    ]
