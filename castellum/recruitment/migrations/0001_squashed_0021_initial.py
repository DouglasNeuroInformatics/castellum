import parler.models
from django.db import migrations
from django.db import models

import castellum.recruitment.models.participations
import castellum.utils.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_type', models.CharField(choices=[('CharField', 'CharField'), ('ChoiceField', 'ChoiceField'), ('MultipleChoiceField', 'MultipleChoiceField'), ('OrderedChoiceField', 'OrderedChoiceField'), ('IntegerField', 'IntegerField'), ('BooleanField', 'BooleanField'), ('DateField', 'DateField'), ('AgeField', 'AgeField')], max_length=64)),
                ('url', models.URLField(blank=True, help_text='URL to a formal definition in an ontology', verbose_name='URL')),
                ('order', models.IntegerField(default=0)),
                ('statistics_rank', models.CharField(blank=True, choices=[('primary', 'primary'), ('secondary', 'secondary')], max_length=16, null=True, unique=True)),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='AttributeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Attribute category',
                'verbose_name_plural': 'Attribute categories',
                'ordering': ['order'],
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='AttributeCategoryTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('label', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name': 'Attribute category Translation',
                'db_table': 'recruitment_attributecategory_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='AttributeChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='AttributeChoiceTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('label', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name': 'attribute choice Translation',
                'db_table': 'recruitment_attributechoice_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='AttributeTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('label', models.CharField(max_length=64)),
                ('_filter_label', models.CharField(blank=True, default='', max_length=64)),
                ('help_text', models.TextField(blank=True, default='')),
            ],
            options={
                'verbose_name': 'attribute Translation',
                'db_table': 'recruitment_attribute_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ExecutionTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('color', models.CharField(choices=[('info', 'Info'), ('success', 'Success'), ('danger', 'Danger'), ('warning', 'Warning'), ('primary', 'Primary')], default='info', max_length=16, verbose_name='Color')),
            ],
        ),
        migrations.CreateModel(
            name='MailBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='Sent date')),
                ('contacted_size', models.PositiveIntegerField()),
                ('reminded', models.DateTimeField(blank=True, null=True, verbose_name='Reminder date')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NewsMailBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='Sent date')),
                ('contacted_size', models.PositiveIntegerField()),
                ('other_size', models.PositiveIntegerField()),
                ('mail_subject', models.CharField(max_length=128, verbose_name='E-mail subject')),
                ('mail_body', models.TextField(verbose_name='E-mail body')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', castellum.utils.fields.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', castellum.utils.fields.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('status', models.IntegerField(choices=[(0, 'not contacted'), (1, 'not reached'), (4, 'follow-up scheduled'), (5, 'awaiting response'), (10, 'recruitment mail sent'), (3, 'participating'), (7, 'participating (dropped out)'), (2, 'excluded'), (6, 'excluded (dropped out)'), (8, 'excluded by cleanup'), (9, 'completed')], default=0, verbose_name='Status of participation')),
                ('exclusion_criteria_checked', models.BooleanField(default=False, verbose_name='Subject may be suitable')),
                ('attempts', models.IntegerField(default=0, verbose_name='Attempts')),
                ('followup_date', castellum.utils.fields.DateField(blank=True, null=True, verbose_name='Follow-up date')),
                ('followup_time', models.TimeField(blank=True, null=True, verbose_name='Follow-up time')),
                ('news_interest', models.IntegerField(choices=[(1, 'not interested'), (2, 'via postal mail'), (3, 'via email')], default=1, verbose_name='Interest in study news')),
            ],
            options={
                'verbose_name': 'Study participation',
                'verbose_name_plural': 'Study participations',
                'permissions': [('conduct_study', 'Can conduct studies'), ('search_participations', 'Can search for any participation'), ('recruit', 'Can recruit')],
            },
        ),
        migrations.CreateModel(
            name='ParticipationConsent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=64, verbose_name='Name')),
                ('file', castellum.utils.fields.RestrictedFileField(upload_to=castellum.recruitment.models.participations.consent_upload_to, verbose_name='File')),
            ],
            options={
                'verbose_name': 'Participation consent',
                'verbose_name_plural': 'Participation consents',
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='ReliabilityEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('was_reliable', models.BooleanField(default=True, verbose_name='Was reliable')),
            ],
            options={
                'verbose_name': 'Reliability entry',
                'verbose_name_plural': 'Reliability entry',
            },
        ),
        migrations.CreateModel(
            name='SubjectFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operator', models.CharField(max_length=64)),
                ('value', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='SubjectFilterGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
