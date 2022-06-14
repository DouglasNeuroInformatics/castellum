from django.db import migrations


def delete_invalid_consentdocuments(apps, schema_editor):
    ConsentDocument = apps.get_model('subjects', 'ConsentDocument')
    ConsentDocument.objects.filter(is_valid=False).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('subjects', '0037_alter_subject_privacy_level'),
    ]

    operations = [
        migrations.RunPython(delete_invalid_consentdocuments),
    ]
