from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('studies', '0066_study_recruitment_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='max_reliability_issues',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Maximum number of reliability issues'),
        ),
    ]
