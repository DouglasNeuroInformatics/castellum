from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pseudonyms', '0010_keypair'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='validate',
            field=models.BooleanField(default=True),
        ),
    ]
