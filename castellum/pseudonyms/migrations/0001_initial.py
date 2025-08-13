import django.db.models.deletion
from django.db import migrations
from django.db import models

import castellum.utils


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(default=castellum.utils.uuid_str, editable=False, max_length=64, unique=True)),
                ('name', models.CharField(blank=True, max_length=64)),
                ('bits', models.PositiveIntegerField(default=40)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Pseudonym',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pseudonym', models.CharField(default=None, max_length=64)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pseudonyms.domain')),
            ],
        ),
    ]
