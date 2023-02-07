from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0054_studysession_reminders_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='principal_investigator',
            field=models.CharField(blank=True, max_length=254, verbose_name='Principal Investigator'),
        ),
    ]
