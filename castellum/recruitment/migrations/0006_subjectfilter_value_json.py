from django.contrib.postgres.fields import JSONField
from django.db import migrations


def copy_value(apps, schema_editor):
    SubjectFilter = apps.get_model('recruitment', 'SubjectFilter')
    for f in SubjectFilter.objects.all():
        f.value = f.value_old
        f.save()


class Migration(migrations.Migration):
    dependencies = [
        ('recruitment', '0005_split_followup'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subjectfilter',
            old_name='value',
            new_name='value_old',
        ),
        migrations.AddField(
            model_name='subjectfilter',
            name='value',
            field=JSONField(default={}),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='subjectfilter',
            name='value_old',
        ),
    ]
