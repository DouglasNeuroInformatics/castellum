from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import migrations

from castellum.contacts.models import Contact


def fix_underage_when_given(apps, schema_editor):
    Consent = apps.get_model('subjects', 'Consent')
    delta = relativedelta(years=settings.CASTELLUM_FULL_AGE)
    for consent in Consent.objects.filter(underage_when_given=None):
        contact = Contact.objects.get(subject_uuid=consent.subject_id)
        if contact.date_of_birth is None:
            continue
        value = contact.date_of_birth + delta > consent.updated_at.date()
        Consent.objects.filter(pk=consent.pk).update(underage_when_given=value)


class Migration(migrations.Migration):
    dependencies = [
        ('subjects', '0050_report_additional_wishes'),
    ]

    operations = [
        migrations.RunPython(fix_underage_when_given),
    ]
