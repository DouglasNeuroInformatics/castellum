from django.db import migrations, models


def create_privacy_levels(apps, schema_editor):
    PrivacyLevel = apps.get_model('castellum_auth', 'PrivacyLevel')

    PrivacyLevel.objects.create(value=0, label='regular')
    PrivacyLevel.objects.create(value=1, label='increased')
    PrivacyLevel.objects.create(value=2, label='high')


class Migration(migrations.Migration):
    dependencies = [
        ('castellum_auth', '0006_remove_user_general_domains'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivacyLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(verbose_name='Value')),
                ('label', models.CharField(max_length=64, verbose_name='Label')),
            ],
        ),
        migrations.RunPython(create_privacy_levels),
    ]
