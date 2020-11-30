from django.db import migrations, models
import django.db.models.deletion


def migrate_data(apps, schema_editor):
    Address = apps.get_model('contacts', 'Address')
    for address in Address.objects.all():
        address.contact = address.contact_set.get()
        address.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0003_subject_id_positive'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='contact',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='contacts.Contact', blank=True, null=True, related_name='+'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='address',
            name='contact',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='contacts.Contact'),
        ),
        migrations.RemoveField(
            model_name='contact',
            name='address',
        ),
    ]
