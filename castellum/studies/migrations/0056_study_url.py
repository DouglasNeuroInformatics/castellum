from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0055_alter_study_principal_investigator'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='url',
            field=models.URLField(blank=True, verbose_name='URL'),
        ),
    ]
