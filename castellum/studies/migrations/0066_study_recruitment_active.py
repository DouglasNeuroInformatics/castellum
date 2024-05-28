import castellum.utils.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0065_study_pseudonyms_delete_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="study",
            name="recruitment_active_after",
            field=castellum.utils.fields.DateField(
                blank=True, null=True, verbose_name="Last subject activity after"
            ),
        ),
        migrations.AddField(
            model_name="study",
            name="recruitment_active_before",
            field=castellum.utils.fields.DateField(
                blank=True, null=True, verbose_name="Last subject activity before"
            ),
        ),
    ]
