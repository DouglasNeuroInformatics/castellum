from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('studies', '0070_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='studysession',
            name='location',
            field=models.CharField(blank=True, max_length=32, verbose_name='Lab/Room'),
        ),
    ]
