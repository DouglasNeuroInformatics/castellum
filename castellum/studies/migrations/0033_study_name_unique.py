import itertools

from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Study = apps.get_model('studies', 'Study')

    for study in Study.objects.reverse():
        if Study.objects.filter(name=study.name).count() > 1:
            for i in itertools.count(2):
                name = '{} {}'.format(study.name, i)
                if not Study.objects.filter(name=name).exists():
                    study.name = name
                    study.save()
                    break


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0032_study_is_filter_trial'),
    ]

    operations = [
        migrations.RunPython(migrate_data),
        migrations.AlterField(
            model_name='study',
            name='name',
            field=models.CharField(max_length=254, unique=True, verbose_name='Name'),
        ),
    ]
