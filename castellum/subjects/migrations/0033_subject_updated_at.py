from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Subject = apps.get_model('subjects', 'Subject')
    Contact = apps.get_model('contacts', 'Contact')

    # re-implementation of constants from model Participation
    UNSUITABLE = 2
    INVITED = 3
    FOLLOWUP_APPOINTED = 4

    subjects = Subject.objects.filter(deceased=False, blocked=False).annotate(
        participation_updated_at=models.Max(
            'participation__updated_at',
            filter=models.Q(
                participation__status__in=[INVITED, UNSUITABLE, FOLLOWUP_APPOINTED],
                participation__excluded_by_cleanup=False,
            ),
        )
    )

    for subject in subjects:
        dates = [subject.updated_at]

        if subject.participation_updated_at:
            dates.append(subject.participation_updated_at.date())

        contact = Contact.objects.filter(subject_uuid=subject.uuid).first()
        if contact:
            dates.append(contact.updated_at)

        most_recent_contact = max(dates)
        if most_recent_contact != subject.updated_at:
            # needs to be update() in order not to set Subject.updated_at to now
            Subject.objects.filter(pk=subject.pk).update(updated_at=most_recent_contact)


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0032_subject_uuid_foreign_key'),
        # this dependency is ineffective because it is about the other database
        ('contacts', '0015_contactcreationrequest_message'),
    ]

    operations = [
        migrations.RunPython(migrate_data),
    ]
