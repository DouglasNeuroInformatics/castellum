import os
import shutil

from django.db import migrations

import castellum.subjects.models
import castellum.utils.fields


def move_files(apps, schema_editor):
    try:
        Timestamp = apps.get_model('storage_timestamps', 'Timestamp')
    except LookupError:
        Timestamp = None

    for model_name in ['Consent', 'ConsentRevision']:
        model = apps.get_model('subjects', model_name)
        for instance in model.objects.exclude(file=''):
            old_name = instance.file.name
            old_path = instance.file.path
            tail = old_name.removeprefix('subjects/')

            instance.file.name = f'subjects/{instance.subject_id}/{tail}'
            instance.save()

            if Timestamp:
                Timestamp.objects.filter(name=old_name).update(name=instance.file.name)
            if os.path.exists(old_path):
                os.makedirs(os.path.dirname(instance.file.path), exist_ok=True)
                shutil.move(old_path, instance.file.path)


class Migration(migrations.Migration):
    dependencies = [
        ('subjects', '0060_participation_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consent',
            name='file',
            field=castellum.utils.fields.RestrictedFileField(blank=True, max_length=140, upload_to=castellum.subjects.models.consent_upload_to, verbose_name='Signed file'),
        ),
        migrations.AlterField(
            model_name='consentrevision',
            name='file',
            field=castellum.utils.fields.RestrictedFileField(blank=True, max_length=140, upload_to=castellum.subjects.models.consent_upload_to, verbose_name='Signed file'),
        ),
        migrations.RunPython(move_files),
    ]
