import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Geolocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('contact', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='contacts.contact')),
            ],
        ),
    ]
