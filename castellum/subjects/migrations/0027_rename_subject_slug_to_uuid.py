import castellum.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0026_subjectcreationrequest'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subject',
            old_name='slug',
            new_name='uuid',
        ),
        migrations.AlterField(
            model_name='subject',
            name='uuid',
            field=models.CharField(default=castellum.utils.uuid_str, max_length=64, unique=True, verbose_name='UUID'),
        ),
    ]
