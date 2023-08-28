from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0049_report'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='support_requested',
        ),
        migrations.AddField(
            model_name='report',
            name='additional_wishes',
            field=models.TextField(
                blank=True, help_text='e.g. Request for a confidential conversation', verbose_name='Additional wishes (optional)'
            ),
        ),
    ]
