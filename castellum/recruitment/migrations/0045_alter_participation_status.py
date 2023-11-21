from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Participation = apps.get_model('recruitment', 'Participation')
    EXCLUDED = 2
    PARTICIPATING = 3
    EXCLUDED_DROPPED_OUT = 6
    PARTICIPATING_DROPPED_OUT = 7

    qs = Participation.objects.filter(status=PARTICIPATING, dropped_out=True)
    qs.update(status=PARTICIPATING_DROPPED_OUT)

    qs = Participation.objects.filter(status=EXCLUDED, dropped_out=True)
    qs.update(status=EXCLUDED_DROPPED_OUT)


class Migration(migrations.Migration):
    dependencies = [
        ("recruitment", "0044_rename_attributedescription_attribute"),
    ]

    operations = [
        migrations.AlterField(
            model_name="participation",
            name="status",
            field=models.IntegerField(
                choices=[
                    (0, "not contacted"),
                    (1, "not reached"),
                    (4, "follow-up scheduled"),
                    (5, "awaiting response"),
                    (3, "participating"),
                    (7, "participating (dropped out)"),
                    (2, "excluded"),
                    (6, "excluded (dropped out)"),
                ],
                default=0,
                verbose_name="Status of participation",
            ),
        ),
        migrations.RunPython(migrate_data),
    ]
