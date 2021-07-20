from django.db import migrations


def migrate_data(apps, schema_editor):
    Contact = apps.get_model('contacts', 'Contact')
    for contact in Contact.objects.all():
        contact.save()  # trigger computation of *_phonetic


class Migration(migrations.Migration):
    dependencies = [
        ('contacts', '0008_alter_contact_gender'),
    ]

    operations = [
        migrations.RunPython(migrate_data),
    ]
