# See also https://stackoverflow.com/questions/42496655

import castellum.castellum_auth.models
from django.db import migrations, models


def set_tokens(apps, schema_editor):
    User = apps.get_model('castellum_auth', 'User')
    for user in User.objects.all():
        user.token = castellum.castellum_auth.models.generate_token()
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('castellum_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='token',
            field=models.CharField(max_length=64, default='empty'),
        ),
        migrations.RunPython(set_tokens),
        migrations.AlterField(
            model_name='user',
            name='token',
            field=models.CharField(
                default=castellum.castellum_auth.models.generate_token,
                max_length=64,
                unique=True,
            ),
        ),
    ]
