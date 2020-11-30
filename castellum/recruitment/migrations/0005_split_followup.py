import castellum.utils.fields
from django.db import migrations, models


def split_followup(model):
    for obj in model.objects.filter(followup__isnull=False):
        obj.followup_date = obj.followup.date()
        obj.followup_time = obj.followup.time()
        obj.save()


def migrate_values(apps, schema_editor):
    split_followup(apps.get_model('recruitment', 'ParticipationRequest'))
    split_followup(apps.get_model('recruitment', 'ParticipationRequestRevision'))


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0004_attributeset_study_type_disinterest'),
    ]

    operations = [
        migrations.AddField(
            model_name='participationrequest',
            name='followup_date',
            field=castellum.utils.fields.DateField(blank=True, null=True, verbose_name='Follow-up date'),
        ),
        migrations.AddField(
            model_name='participationrequest',
            name='followup_time',
            field=models.TimeField(blank=True, null=True, verbose_name='Follow-up time'),
        ),
        migrations.AddField(
            model_name='participationrequestrevision',
            name='followup_date',
            field=castellum.utils.fields.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='participationrequestrevision',
            name='followup_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.RunPython(migrate_values),
        migrations.RemoveField(
            model_name='participationrequest',
            name='followup',
        ),
        migrations.RemoveField(
            model_name='participationrequestrevision',
            name='followup',
        ),
    ]
