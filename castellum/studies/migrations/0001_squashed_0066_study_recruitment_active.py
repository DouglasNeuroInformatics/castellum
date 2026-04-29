import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations
from django.db import models

import castellum.studies.models
import castellum.utils.fields
import castellum.utils.forms


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ('studies', '0001_squashed_0035_initial'),
        ('studies', '0036_resource_managers'),
        ('studies', '0037_resource_url'),
        ('studies', '0038_delete_studytypeeventfeed'),
        ('studies', '0039_rm_data_sensitivity'),
        ('studies', '0040_remove_study_custom_filter'),
        ('studies', '0041_alter_study_consent'),
        ('studies', '0042_alter_resource_url'),
        ('studies', '0043_studysession_schedule_updated_at'),
        ('studies', '0044_alter_studysession_resource'),
        ('studies', '0045_help_texts'),
        ('studies', '0046_rename_study_is_onetime_invitation'),
        ('studies', '0047_change_upload_to'),
        ('studies', '0048_alter_study_geo_filter'),
        ('studies', '0049_remove_study_announce_status_changes'),
        ('studies', '0050_remove_study_exclusion_criteria'),
        ('studies', '0051_remove_study_is_anonymous_invitation_data'),
        ('studies', '0052_remove_study_is_anonymous_invitation'),
        ('studies', '0053_remove_study_snapshot'),
        ('studies', '0054_studysession_reminders_enabled'),
        ('studies', '0055_alter_study_principal_investigator'),
        ('studies', '0056_study_url'),
        ('studies', '0057_alter_study_contact_person'),
        ('studies', '0058_studylock'),
        ('studies', '0059_remove_studysession_reminders_enabled_and_more'),
        ('studies', '0060_study_included_studies'),
        ('studies', '0061_alter_study_is_exclusive'),
        ('studies', '0062_alter_study_options'),
        ('studies', '0063_alter_resource_id_alter_study_id_alter_studygroup_id_and_more'),
        ('studies', '0064_study_created_at_study_updated_at'),
        ('studies', '0065_study_pseudonyms_delete_date'),
        ('studies', '0066_study_recruitment_active'),
    ]

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pseudonyms', '0001_squashed_initial'),
        ('recruitment', '0001_squashed_0021_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('url', models.URLField(blank=True, help_text='Any "{start}"- and "{end}"-tags included in the URL will automatically be replaced by the relevant datetime in ISO 8601 format.', verbose_name='Calendar URL')),
                ('color', castellum.utils.fields.ColorField(default='#000000', max_length=7, verbose_name='Calendar color')),
                ('managers', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='Managers')),
            ],
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=254, unique=True, verbose_name='Name')),
                ('contact_person', models.CharField(max_length=254, verbose_name='Contact person')),
                ('email', models.EmailField(max_length=128, verbose_name='Email-address')),
                ('phone', castellum.utils.fields.PhoneNumberField(max_length=32, region=None, verbose_name='Phone number')),
                ('principal_investigator', models.CharField(blank=True, max_length=254, verbose_name='Principal Investigator')),
                ('affiliated_scientists', models.CharField(blank=True, max_length=254, verbose_name='Affiliated Scientists')),
                ('affiliated_research_assistants', models.CharField(blank=True, max_length=254, verbose_name='Affiliated Research Assistants')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('url', models.URLField(blank=True, verbose_name='URL')),
                ('previous_status', models.SmallIntegerField(choices=[(0, 'Draft'), (1, 'Execution'), (2, 'Finished')], default=0, verbose_name='Previous status')),
                ('status', models.SmallIntegerField(choices=[(0, 'Draft'), (1, 'Execution'), (2, 'Finished')], default=0, verbose_name='Status')),
                ('min_subject_count', models.PositiveIntegerField(default=0, verbose_name='Required number of subjects')),
                ('session_instructions', models.TextField(blank=True, help_text='Please describe any requirements for carrying out the sessions listed below. For example, specify time intervals between sessions that need to be considered for booking appointments.', verbose_name='Session instructions')),
                ('sessions_start', castellum.utils.fields.DateField(blank=True, null=True, verbose_name='Start of data collection')),
                ('sessions_end', castellum.utils.fields.DateField(blank=True, null=True, verbose_name='End of data collection')),
                ('recruitment_text', models.TextField(blank=True, help_text='This text will be used during recruitment dialogue. Thus, please describe the study from the perspective of recruiters and potential participants: What is it about? How long will it take? Are there any potential benefits or risks for participants? If applicable, also present the amount of expense allowance and related requirements.', verbose_name='Recruitment text')),
                ('pseudonyms_delete_date', castellum.utils.fields.DateField(blank=True, help_text='This date is usually defined in the ethics application and the study consent form. Entering it here is purely informational. The pseudonym lists will not be deleted automatically.', null=True, verbose_name='Date when pseudonym lists should be deleted')),
                ('advanced_filtering', models.BooleanField(default=False, help_text='By default you can create only one filtergroup in which all the filters are joined by AND operator. Advanced filtering allows you to create multiple filtergroups which are joined by OR operator.', verbose_name='Advanced filtering')),
                ('geo_filter', castellum.utils.fields.RestrictedFileField(blank=True, help_text='A GeoJSON file that contains (multi)polygons. Only subjects who live inside the polygons will be considered for this study.', upload_to=castellum.studies.models.geofilter_upload_to, validators=[castellum.utils.forms.JsonFileValidator({'$defs': {'Feature': {'properties': {'geometry': {'oneOf': [{'$ref': '#/$defs/Polygon'}, {'$ref': '#/$defs/MultiPolygon'}], 'properties': {'type': {'enum': ['Polygon', 'MultiPolygon'], 'type': 'string'}}, 'type': 'object'}, 'properties': {'oneOf': [{'type': 'null'}, {'type': 'object'}]}, 'type': {'const': 'Feature', 'type': 'string'}}, 'required': ['type', 'properties', 'geometry'], 'type': 'object'}, 'FeatureCollection': {'properties': {'features': {'items': {'$ref': '#/$defs/Feature'}, 'type': 'array'}, 'type': {'const': 'FeatureCollection', 'type': 'string'}}, 'required': ['type', 'features'], 'type': 'object'}, 'MultiPolygon': {'properties': {'coordinates': {'items': {'$ref': '#/$defs/PolygonCoordinates'}, 'type': 'array'}, 'type': {'const': 'MultiPolygon', 'type': 'string'}}, 'required': ['type', 'coordinates'], 'type': 'object'}, 'Polygon': {'properties': {'coordinates': {'$ref': '#/$defs/PolygonCoordinates'}, 'type': {'const': 'Polygon', 'type': 'string'}}, 'required': ['type', 'coordinates'], 'type': 'object'}, 'PolygonCoordinates': {'items': {'items': {'items': {'type': 'number'}, 'minItems': 2, 'type': 'array'}, 'minItems': 4, 'type': 'array'}, 'type': 'array'}, 'geofilter': {'oneOf': [{'$ref': '#/$defs/Feature'}, {'$ref': '#/$defs/FeatureCollection'}], 'properties': {'type': {'enum': ['Feature', 'FeatureCollection'], 'type': 'string'}}, 'type': 'object'}}, '$schema': 'http://json-schema.org/draft-07/schema#'}, '#/$defs/geofilter')], verbose_name='Geo filter file')),
                ('is_exclusive', models.BooleanField(default=False, help_text='When set, this ensures that potential subjects for this study will not be recruited in other studies. Please note that this may hinder other researchers in finding enough participants. You can free up participants for other studies by using the "completed" participation status.', verbose_name='Exclusive subjects')),
                ('complete_matches_only', models.BooleanField(default=False, help_text='By default, filters may include subjects with incomplete attributes. This feature is supposed to improve the quality of the database by asking recruiters to fill missing values on the go. Only allowing complete filter matches can speed up individual recruitments but may deteriorate the quality of the database as a whole. Furthermore, this reduces the number of potential subjects.', verbose_name='Complete filter matches only')),
                ('recruitment_active_after', castellum.utils.fields.DateField(blank=True, null=True, verbose_name='Last activity after')),
                ('recruitment_active_before', castellum.utils.fields.DateField(blank=True, null=True, verbose_name='Last activity before')),
                ('is_filter_trial', models.BooleanField(default=False, help_text='Use this if you only want to see how many subjects would match a specific study and filter configuration without actually intending to recruit.', verbose_name='Is a filter trial')),
                ('consent', castellum.utils.fields.RestrictedFileField(blank=True, help_text='A blueprint of the study consent. This file can be obtained (and printed) later by recruiters or conductors.', upload_to=castellum.studies.models.consent_upload_to, verbose_name='Study consent')),
                ('mail_subject', models.CharField(blank=True, max_length=254, verbose_name='Email subject')),
                ('mail_body', models.TextField(blank=True, help_text='Any "{name}"-tags included in the email-body will automatically be replaced with the full name of the subject.', verbose_name='Email body')),
                ('excluded_studies', models.ManyToManyField(blank=True, help_text='Participants from excluded studies will be excluded from recruitment for this study.', related_name='excluded_by', to='studies.study', verbose_name='Excluded studies')),
                ('exportable_attributes', models.ManyToManyField(blank=True, help_text='This allows to download these attributes as a data file in study execution, e.g. to use a specific attribute for the analysis.', related_name='+', to='recruitment.attribute', verbose_name='Exportable recruitment attributes')),
                ('general_domains', models.ManyToManyField(blank=True, limit_choices_to={'object_id': None}, to='pseudonyms.domain', verbose_name='General pseudonym lists')),
                ('included_studies', models.ManyToManyField(blank=True, help_text='If selected, only participants from included studies will be considered in the recruitment for this study. Note that reusing data from those studies is not always possible, e.g. because the study consent does not allow data reuse or because the pseudonyms have already been deleted.', related_name='included_by', to='studies.study', verbose_name='Included studies')),
            ],
            options={
                'ordering': ['name'],
                'permissions': [('access_study', 'Can access studies'), ('approve_study', 'Can approve studies'), ('view_audit_trail', 'Can view audit trail')],
            },
        ),
        migrations.CreateModel(
            name='StudyGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='name')),
                ('permissions', models.ManyToManyField(blank=True, to='auth.permission', verbose_name='permissions')),
            ],
        ),
        migrations.CreateModel(
            name='StudyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exclusion_criteria', models.TextField(blank=True, verbose_name='Additional subject characteristics that should be verified during recruitment')),
                ('export_key', models.CharField(blank=True, choices=[('Online', 'Online'), ('Behavioral lab', 'Behavioral lab'), ('MRI', 'MRI'), ('Simulation', 'Simulation'), ('EEG', 'EEG')], max_length=32, verbose_name='Export key')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StudyTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studies.study')),
            ],
        ),
        migrations.CreateModel(
            name='StudySession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('duration', models.PositiveIntegerField(verbose_name='Duration of a session in minutes')),
                ('first_reminder_days', models.PositiveIntegerField(blank=True, default=3, null=True, verbose_name='First reminder')),
                ('second_reminder_days', models.PositiveIntegerField(blank=True, default=None, null=True, verbose_name='Second reminder')),
                ('reminder_text', models.TextField(blank=True, verbose_name='Additional text for reminder emails')),
                ('schedule_id', models.CharField(blank=True, max_length=64, null=True, unique=True, verbose_name='External schedule ID')),
                ('schedule_updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('resources', models.ManyToManyField(blank=True, to='studies.resource', verbose_name='Resources')),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studies.study')),
                ('type', models.ManyToManyField(blank=True, to='studies.studytype', verbose_name='Type')),
            ],
        ),
        migrations.CreateModel(
            name='StudyMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groups', models.ManyToManyField(blank=True, related_name='+', to='studies.studygroup')),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studies.study')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('study', 'user')},
            },
        ),
        migrations.CreateModel(
            name='StudyLock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='studies.study')),
            ],
        ),
        migrations.AddField(
            model_name='study',
            name='members',
            field=models.ManyToManyField(through='studies.StudyMembership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='StudyTypeTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('label', models.CharField(max_length=64, verbose_name='Label')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='studies.studytype')),
            ],
            options={
                'verbose_name': 'study type Translation',
                'db_table': 'studies_studytype_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
        ),
    ]
