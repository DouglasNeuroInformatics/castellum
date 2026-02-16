# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ('pseudonyms', '0002_squashed_0009_alter_domain_id_alter_pseudonym_id'),
        ('studies', '0071_studysession_location'),
        ('subjects', '0063_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='SSHKeyPair',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('public_key', models.TextField()),
                ('private_key', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('shredded_at', models.DateTimeField(blank=True, null=True)),
                ('algorithm', models.CharField(default='ed25519', max_length=16)),
                (
                    'study',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='ssh_key_pairs',
                        to='studies.study',
                    ),
                ),
                (
                    'subject',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='ssh_key_pairs',
                        to='subjects.subject',
                    ),
                ),
            ],
            options={
                'verbose_name': 'SSH Key Pair',
                'verbose_name_plural': 'SSH Key Pairs',
                'unique_together': {('study', 'subject')},
            },
        ),
    ]
