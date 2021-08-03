from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0032_study_is_filter_trial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='name',
            field=models.CharField(max_length=254, unique=True, verbose_name='Name'),
        ),
    ]
