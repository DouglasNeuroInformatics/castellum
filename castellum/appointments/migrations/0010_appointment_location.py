from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('appointments', '0002_squashed_0009_alter_appointment_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='location',
            field=models.CharField(blank=True, max_length=32, verbose_name='Lab/Room'),
        ),
    ]
