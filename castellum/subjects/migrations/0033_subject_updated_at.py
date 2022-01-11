from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Subject = apps.get_model('subjects', 'Subject')
    Contact = apps.get_model('contacts', 'Contact')

    # re-implementation of constants from model Participation
    UNSUITABLE = 2
    INVITED = 3
    FOLLOWUP_APPOINTED = 4

    subjects = Subject.objects.filter(
        deceased=False, blocked=False
    ).annotate(
        participation_updated_at=models.Max(
            'participation__updated_at',
            filter=models.Q(
                participation__status__in=[INVITED, UNSUITABLE, FOLLOWUP_APPOINTED],
                participation__excluded_by_cleanup=False,
            )
        )
    )

    for subject in subjects:
        contact = Contact.objects.filter(subject_uuid=subject.pk).first()
        if contact:
            contact_updated_at = contact.updated_at
        else:
            contact_updated_at = None

        dates = [subject.updated_at, contact_updated_at, subject.participation_updated_at.date()]
        most_recent_contact = max(date for date in dates if date)

        if most_recent_contact != subject.updated_at:
            # needs to be update() in order not to set Subject.updated_at to now
            Subject.objects.filter(uuid=subject.uuid).update(updated_at=most_recent_contact)


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0032_subject_uuid_foreign_key'),

        # this dependency is ineffective because it is about the other database
        ('contacts', '0015_contactcreationrequest_message'),
    ]

    operations = [
        migrations.RunPython(migrate_data),
    ]
