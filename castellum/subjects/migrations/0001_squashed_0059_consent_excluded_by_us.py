import uuid

import django.core.serializers.json
import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models

import castellum.utils.fields


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ('subjects', '0001_squashed_0028_initial'),
        ('subjects', '0029_subjectcreationrequest_data_is_deleted'),
        ('subjects', '0030_subject_uuid'),
        ('subjects', '0031_subject_uuid_primary_key'),
        ('subjects', '0032_subject_uuid_foreign_key'),
        ('subjects', '0033_subject_updated_at'),
        ('subjects', '0034_help_texts'),
        ('subjects', '0035_consent_underage_when_given'),
        ('subjects', '0036_rename_subject_onetime_invitation_disinterest'),
        ('subjects', '0037_alter_subject_privacy_level'),
        ('subjects', '0038_delete_invalid_consentdocuments'),
        ('subjects', '0039_remove_consentdocument_is_valid'),
        ('subjects', '0040_consentdocument_name'),
        ('subjects', '0041_alter_consent_document'),
        ('subjects', '0042_alter_consent'),
        ('subjects', '0043_consent_file'),
        ('subjects', '0044_remove_subject_anonymous_invitation_disinterest'),
        ('subjects', '0045_delete_subjectnote'),
        ('subjects', '0046_remove_subject_consent_waiting_since'),
        ('subjects', '0047_alter_consentdocument_options'),
        ('subjects', '0048_remove_subject_additional_suitability_document'),
        ('subjects', '0049_report'),
        ('subjects', '0050_report_additional_wishes'),
        ('subjects', '0051_fix_consent_underage_when_given'),
        ('subjects', '0052_alter_report_user'),
        ('subjects', '0053_alter_report_subject'),
        ('subjects', '0054_alter_subject_options'),
        ('subjects', '0055_alter_consent_id_alter_consentdocument_id_and_more'),
        ('subjects', '0056_consent_full_age_notified'),
        ('subjects', '0057_consentdocument_is_valid'),
        ('subjects', '0058_consentrevision'),
        ('subjects', '0059_consent_excluded_by_us'),
    ]

    dependencies = [
        ('studies', '0001_squashed_0066_study_recruitment_active'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsentDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=254, verbose_name='Name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('is_valid', models.BooleanField(default=True, verbose_name='Is valid')),
                ('is_deprecated', models.BooleanField(default=False, verbose_name='Is deprecated')),
                ('file', castellum.utils.fields.RestrictedFileField(blank=True, upload_to='consent/', verbose_name='File')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='SubjectCreationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Updated at')),
                ('delete_url', models.URLField(blank=True, max_length=128, null=True, unique=True, verbose_name='Delete URL')),
                ('source', models.CharField(blank=True, max_length=128, verbose_name='Data source')),
                ('data_is_deleted', models.BooleanField(default=False, verbose_name='Personal data has been deleted')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Updated at')),
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='UUID')),
                ('attributes', models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder, verbose_name='Recruitment attributes')),
                ('privacy_level', models.FloatField(default=0.0, help_text='Users need at least this level to access this subject', verbose_name='Privacy level')),
                ('to_be_deleted', models.DateField(blank=True, help_text='The subject wants all data about them to be deleted or fully anonymized. This includes all data in Castellum and possibly all data collected in studies (if no other legal bases apply, for example retention periods). Furthermore, the subject has explicitly rejected the option to only withdraw recruitment consent instead. When a subject requests GDPR deletion please use this option to set the processing of their request in motion.', null=True, verbose_name='To be deleted')),
                ('to_be_deleted_notified', models.BooleanField(default=False)),
                ('export_requested', models.DateField(blank=True, help_text='The subject wants to receive an export of all data we have stored about them. This includes all data in Castellum and all data collected in studies. When a subject requests GDPR export please use this option to set the processing of their request in motion.', null=True, verbose_name='Export requested')),
                ('deceased', models.BooleanField(default=False, verbose_name='Subject is deceased')),
                ('blocked', models.BooleanField(default=False, help_text='The person has been blocked due to inappropriate behaviour. They will neither be considered for recruitment, nor contacted as a legal representative. Blocking this person does not automatically block any represented subjects nor co-representatives. They may thus still receive information about the recruitment process.', verbose_name='Subject is blocked')),
                ('source', models.CharField(blank=True, max_length=128, verbose_name='Data source')),
                ('not_available_until', castellum.utils.fields.DateTimeField(blank=True, null=True, verbose_name='not available until')),
                ('study_type_disinterest', models.ManyToManyField(blank=True, related_name='+', to='studies.studytype', verbose_name='Does not want to participate or is permanently unsuitable for the following study types')),
            ],
            options={
                'verbose_name': 'Subject',
                'permissions': [('export_subject', 'Can export all data related to a subject'), ('view_audit_trail', 'Can view audit trail')],
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('additional_wishes', models.TextField(blank=True, help_text='e.g. Request for a confidential conversation', verbose_name='Additional wishes (optional)')),
                ('subject', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='subjects.subject', verbose_name='Subject')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='ExportAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Created at')),
                ('created_by', models.CharField(max_length=150, verbose_name='Created by')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject')),
            ],
            options={
                'verbose_name': 'Export answer',
                'verbose_name_plural': 'Export answers',
            },
        ),
        migrations.CreateModel(
            name='ConsentRevision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('underage_when_given', models.BooleanField(null=True, verbose_name='Underage when given')),
                ('file', castellum.utils.fields.RestrictedFileField(blank=True, upload_to='subjects/consents/', verbose_name='Signed file')),
                ('excluded_by_us', models.BooleanField(default=False, verbose_name='Excluded by us')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('document', models.ForeignKey(blank=True, limit_choices_to={'is_valid': True}, null=True, on_delete=django.db.models.deletion.CASCADE, to='subjects.consentdocument', verbose_name='Document')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject')),
            ],
            options={
                'verbose_name': 'Consent revision',
                'verbose_name_plural': 'Consent revisions',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Consent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('underage_when_given', models.BooleanField(null=True, verbose_name='Underage when given')),
                ('file', castellum.utils.fields.RestrictedFileField(blank=True, upload_to='subjects/consents/', verbose_name='Signed file')),
                ('excluded_by_us', models.BooleanField(default=False, verbose_name='Excluded by us')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('full_age_notified_1', models.BooleanField(default=False, verbose_name='First full age expiration notification sent')),
                ('full_age_notified_2', models.BooleanField(default=False, verbose_name='Second full age expiration notification sent')),
                ('document', models.ForeignKey(blank=True, limit_choices_to={'is_valid': True}, null=True, on_delete=django.db.models.deletion.CASCADE, to='subjects.consentdocument', verbose_name='Document')),
                ('subject', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject')),
            ],
            options={
                'verbose_name': 'Consent',
            },
        ),
    ]
