import castellum.pseudonyms.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pseudonyms', '0002_squashed_0009_alter_domain_id_alter_pseudonym_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeyPair',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'private_key',
                    models.BinaryField(
                        default=castellum.pseudonyms.models.generate_private_key
                    ),
                ),
                (
                    'pseudonym',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='pseudonyms.pseudonym',
                    ),
                ),
            ],
        ),
    ]
