from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0059_remove_studysession_reminders_enabled_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="study",
            name="included_studies",
            field=models.ManyToManyField(
                blank=True,
                help_text="If selected, only participants from included studies will be considered in the recruitment for this study. Note that reusing data from those studies is not always possible, e.g. because the study consent does not allow data reuse or because the pseudonyms have already been deleted.",
                related_name="+",
                to="studies.study",
                verbose_name="Included studies",
            ),
        ),
        migrations.AlterField(
            model_name="study",
            name="excluded_studies",
            field=models.ManyToManyField(
                blank=True,
                help_text="Participants from excluded studies will be excluded from recruitment for this study.",
                related_name="+",
                to="studies.study",
                verbose_name="Excluded studies",
            ),
        ),
    ]
