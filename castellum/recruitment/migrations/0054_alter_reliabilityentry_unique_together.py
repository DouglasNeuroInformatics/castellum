from django.db import migrations
from django.db import models


def migrate_data(apps, schema_editor):
    ReliabilityEntry = apps.get_model('recruitment', 'ReliabilityEntry')

    qs = (
        ReliabilityEntry.objects
        .values('study', 'subject')
        .annotate(count=models.Count('id'))
        .filter(count__gt=1)
    )

    for participation in qs:
        entries = ReliabilityEntry.objects.filter(
            study=participation['study'],
            subject=participation['subject'],
        )

        keep = entries[0]
        for entry in entries:
            if not entry.was_reliable:
                keep = entry
                break

        entries.exclude(pk=keep.pk).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('recruitment', '0053_alter_relationtype_options_relationtype_order'),
        ('studies', '0069_parler'),
        ('subjects', '0062_consent_expire_at'),
    ]

    operations = [
        migrations.RunPython(migrate_data),
        migrations.AlterUniqueTogether(
            name='reliabilityentry',
            unique_together={('study', 'subject')},
        ),
    ]
