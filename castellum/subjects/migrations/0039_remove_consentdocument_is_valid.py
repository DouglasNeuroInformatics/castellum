from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('subjects', '0038_delete_invalid_consentdocuments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consentdocument',
            name='is_valid',
        ),
    ]
