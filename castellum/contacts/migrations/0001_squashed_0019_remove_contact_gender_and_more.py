import django.db.models.deletion
from django.db import migrations
from django.db import models

import castellum.utils.fields


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ('contacts', '0001_squashed_0012_initial'),
        ('contacts', '0013_contact_subject_uuid'),
        ('contacts', '0014_contactcreationrequest_phone_number'),
        ('contacts', '0015_contactcreationrequest_message'),
        ('contacts', '0016_remove_contact_preferred_contact_method'),
        ('contacts', '0017_alter_address_id_alter_contact_id_and_more'),
        ('contacts', '0018_alter_address_zip_code'),
        ('contacts', '0019_remove_contact_gender_and_more'),
    ]

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ContactCreationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Updated at')),
                ('first_name', models.CharField(max_length=64, verbose_name='First name')),
                ('last_name', models.CharField(max_length=64, verbose_name='Last name')),
                ('title', models.CharField(blank=True, max_length=64, verbose_name='Title')),
                ('date_of_birth', castellum.utils.fields.DateField(blank=True, null=True, verbose_name='Date of birth')),
                ('phone_number', castellum.utils.fields.PhoneNumberField(blank=True, max_length=32, region=None, verbose_name='Phone number')),
                ('subject_id', models.PositiveIntegerField(default=None, editable=False, unique=True)),
                ('email', models.EmailField(max_length=128, verbose_name='Email')),
                ('message', models.TextField(blank=True, verbose_name='Message')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Street',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Updated at')),
                ('first_name', models.CharField(max_length=64, verbose_name='First name')),
                ('last_name', models.CharField(max_length=64, verbose_name='Last name')),
                ('title', models.CharField(blank=True, max_length=64, verbose_name='Title')),
                ('date_of_birth', castellum.utils.fields.DateField(blank=True, null=True, verbose_name='Date of birth')),
                ('phone_number', castellum.utils.fields.PhoneNumberField(blank=True, max_length=32, region=None, verbose_name='Phone number')),
                ('subject_uuid', models.UUIDField(default=None, editable=False, unique=True)),
                ('first_name_phonetic', models.CharField(default=None, editable=False, max_length=128)),
                ('last_name_phonetic', models.CharField(default=None, editable=False, max_length=128)),
                ('email', models.EmailField(blank=True, max_length=128, verbose_name='Email')),
                ('phone_number_alternative', castellum.utils.fields.PhoneNumberField(blank=True, max_length=32, region=None, verbose_name='Phone number alternative')),
                ('legal_representatives', models.ManyToManyField(blank=True, related_name='legal_representative_of', to='contacts.contact', verbose_name='Legal representatives')),
            ],
            options={
                'verbose_name': 'Contact data',
                'verbose_name_plural': 'Contact data',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=64, verbose_name='Country')),
                ('city', models.CharField(max_length=128, verbose_name='City')),
                ('zip_code', models.CharField(max_length=12, verbose_name='Postal code')),
                ('street', models.CharField(max_length=128, verbose_name='Street')),
                ('house_number', models.CharField(max_length=16, verbose_name='House number')),
                ('additional_information', models.CharField(blank=True, max_length=32, verbose_name='Additional address information')),
                ('contact', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='contacts.contact')),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Addresses',
                'ordering': ['country', 'city', 'zip_code', 'street', 'house_number', 'additional_information'],
            },
        ),
    ]
