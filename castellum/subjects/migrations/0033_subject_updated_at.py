from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Subject = apps.get_model('subjects', 'Subject')
    Contact = apps.get_model('contacts', 'Contact')
    # re-implementation of constants from model Participation
    UNSUITABLE = 2
    INVITED = 3
    FOLLOWUP_APPOINTED = 4


    for subject in Subject.objects.all():
        if not subject.deceased or subject.blocked:
            contacted_status = [INVITED, UNSUITABLE, FOLLOWUP_APPOINTED]
            if subject.participation_set:
                participation_updated_at = max(subject.participation_set.filter(
                    status__in=contacted_status,
                    excluded_by_cleanup=False,
                ).values_list('updated_at', flat=True))
            else:
                participation_updated_at = None

            contact = Contact.objects.filter(subject_uuid=subject.pk)
            if contact.exists():
                contact_updated_at = Contact.objects.get(subject_uuid=subject.pk).updated_at
            else:
                contact_updated_at = None

            most_recent_contact = max(subject.updated_at, contact_updated_at, participation_updated_at)
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
