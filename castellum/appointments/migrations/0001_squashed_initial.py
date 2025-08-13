from django.db import migrations
from django.db import models

import castellum.utils.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', castellum.utils.fields.DateTimeField(verbose_name='Start')),
                ('first_reminder_sent', models.BooleanField(default=False, verbose_name='First reminder sent')),
                ('second_reminder_sent', models.BooleanField(default=False, verbose_name='Second reminder sent')),
            ],
            options={
                'verbose_name': 'Appointment',
                'ordering': ['start'],
                'permissions': [('view_current_appointments', 'Can view current appointments')],
            },
        ),
    ]
