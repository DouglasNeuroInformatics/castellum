import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations
from django.db import models

import castellum.castellum_auth.models
import castellum.utils.fields


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ('castellum_auth', '0001_initial'),
        ('castellum_auth', '0002_user_token'),
        ('castellum_auth', '0003_first_name_length'),
        ('castellum_auth', '0004_user_general_domains'),
        ('castellum_auth', '0005_remove_user_logout_timeout'),
        ('castellum_auth', '0006_remove_user_general_domains'),
        ('castellum_auth', '0007_user_description'),
        ('castellum_auth', '0008_alter_user_id'),
    ]

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('language', models.CharField(blank=True, choices=[('de', 'German'), ('en', 'English')], max_length=5, verbose_name='Language')),
                ('expiration_date', castellum.utils.fields.DateTimeField(blank=True, null=True, verbose_name='Expiration date')),
                ('token', models.CharField(default=castellum.castellum_auth.models.generate_token, max_length=64, unique=True)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['username'],
                'permissions': [('privacy_level_1', 'Can access privacy level 1'), ('privacy_level_2', 'Can access privacy level 2')],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
