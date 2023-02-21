from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0056_study_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='contact_person',
            field=models.CharField(max_length=254, verbose_name='Contact person'),
        ),
    ]
