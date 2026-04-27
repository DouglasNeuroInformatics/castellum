from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contacts', '0020_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockHash',
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
                ('hash', models.BinaryField(max_length=32)),
            ],
        ),
    ]
