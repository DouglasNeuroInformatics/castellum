from django.conf import settings
from django.db import migrations, models

from castellum.pseudonyms.helpers import get_subject


def migrate_value(apps, schema_editor):
    Contact = apps.get_model('contacts', 'Contact')
    for contact in Contact.objects.all():
        domain = settings.CASTELLUM_DOMAINS['contact']['key']
        subject = get_subject(domain, contact.pseudonym)
        contact.subject_id = subject.pk
        contact.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='subject_id',
            field=models.IntegerField(default=None, editable=False, unique=True, null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='subject_id',
            field=models.IntegerField(default=None, editable=False, unique=True),
        ),
        migrations.RemoveField(
            model_name='contact',
            name='pseudonym',
        ),
    ]
