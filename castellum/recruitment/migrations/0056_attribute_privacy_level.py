from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('recruitment', '0055_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='privacy_level',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
