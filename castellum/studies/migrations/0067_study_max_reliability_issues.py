from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ('studies', '0066_study_recruitment_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='max_reliability_issues',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='This refers to the number of studies that would not invite this subject again because they were unreliable.',
                null=True,
                verbose_name='Maximum number of issues in previous studies',
            ),
        ),
    ]
