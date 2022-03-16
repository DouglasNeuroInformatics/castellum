from django.db import migrations, models
import django.db.models.deletion


def get_privacy_level(user):
    for level in range(2, 0, -1):
        if user.user_permissions.filter(
            content_type__app_label='castellum_auth',
            codename='privacy_level_{}'.format(level)
        ).exists():
            return level
    return 0


def create_privacy_levels(apps, schema_editor):
    PrivacyLevel = apps.get_model('castellum_auth', 'PrivacyLevel')

    PrivacyLevel.objects.create(value=0, label='regular')
    PrivacyLevel.objects.create(value=1, label='increased')
    PrivacyLevel.objects.create(value=2, label='high')


def set_privacy_levels(apps, schema_editor):
    PrivacyLevel = apps.get_model('castellum_auth', 'PrivacyLevel')
    User = apps.get_model('castellum_auth', 'User')

    for user in User.objects.all():
        value = get_privacy_level(user)
        user.privacy_level = PrivacyLevel.objects.get(value=value)
        user.save()


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

        migrations.AddField(
            model_name='user',
            name='privacy_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='castellum_auth.privacylevel', null=True),
        ),
        migrations.RunPython(set_privacy_levels),
        migrations.AlterField(
            model_name='user',
            name='privacy_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='castellum_auth.privacylevel'),
        ),
    ]
