import uuid

from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Subject = apps.get_model('subjects', 'Subject')
    Contact = apps.get_model('contacts', 'Contact')

    for contact in Contact.objects.all():
        contact.subject_uuid = Subject.objects.get(uuid=self.subject_id).uuid
        contact.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0009_phonetic_diacritics'),
    ]

    operations = [

        migrations.AddField(
            model_name='contact',
            name='subject_uuid',
            field=models.UUIDField(default=None, editable=False),
        ),
        migrations.RunPython(migrate_data),
        migrations.RemoveField(
            model_name='contact',
            name='subject_id',
        ),
        migrations.RenameField(
            model_name='contact',
            old_name='subject_uuid',
            new_name='subject_id',
        ),
        migrations.AlterField(
            model_name='contact',
            name='subject_id',
            field=models.UUIDField(default=None, editable=False, unique=True),
        ),

    ]
