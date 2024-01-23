from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("subjects", "0050_report_additional_wishes"),
    ]

    operations = [
        migrations.AddField(
            model_name="consentdocument",
            name="is_valid",
            field=models.BooleanField(default=True, verbose_name="Is valid"),
        ),
        migrations.AlterField(
            model_name="consent",
            name="document",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"is_valid": True},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="subjects.consentdocument",
                verbose_name="Document",
            ),
        ),
    ]
