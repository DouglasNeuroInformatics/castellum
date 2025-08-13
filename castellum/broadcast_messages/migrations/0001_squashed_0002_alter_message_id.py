from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ('broadcast_messages', '0001_initial'),
        ('broadcast_messages', '0002_alter_message_id'),
    ]

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=254, verbose_name='Content')),
                ('level', models.CharField(choices=[('success', 'Success'), ('info', 'Info'), ('warning', 'Warning'), ('danger', 'Danger')], max_length=16, verbose_name='Message level')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
        ),
    ]
