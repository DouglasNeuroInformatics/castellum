from django.conf import settings
from django.db import migrations
from django.db import models
from django.utils import timezone

from castellum.recruitment import filter_queries


def set_values(apps, schema_editor):
    Subject = apps.get_model('subjects', 'Subject')
    subjects = Subject.objects.filter(
        created_at__gte=timezone.now() - settings.CASTELLUM_CONSENT_REVIEW_PERIOD
    ).filter(
        filter_queries.has_consent()
    )

    for subject in subjects:
        subject.do_not_delete_until = subject.created_at + settings.CASTELLUM_CONSENT_REVIEW_PERIOD
        subject.save()


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0040_subject_do_not_delete_until'),
    ]

    operations = [
        migrations.RunPython(set_values, atomic=False)
    ]
