from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0061_alter_study_is_exclusive"),
    ]

    operations = [
        migrations.AddField(
            model_name="study",
            name="recruitment_active_after",
            field=models.DateField(
                blank=True, null=True, verbose_name="Last subject activity after"
            ),
        ),
        migrations.AddField(
            model_name="study",
            name="recruitment_active_before",
            field=models.DateField(
                blank=True, null=True, verbose_name="Last subject activity before"
            ),
        ),
    ]
