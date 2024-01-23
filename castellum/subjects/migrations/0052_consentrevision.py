import castellum.utils.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("subjects", "0051_consentdocument_is_valid"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConsentRevision",
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
                    "underage_when_given",
                    models.BooleanField(null=True, verbose_name="Underage when given"),
                ),
                (
                    "file",
                    castellum.utils.fields.RestrictedFileField(
                        blank=True,
                        upload_to="subjects/consents/",
                        verbose_name="Signed file",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "document",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"is_valid": True},
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="subjects.consentdocument",
                        verbose_name="Document",
                    ),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="subjects.subject",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "ordering": ["created_at"],
                "verbose_name": "Consent revision",
                "verbose_name_plural": "Consent revisions",
            },
        ),
    ]
