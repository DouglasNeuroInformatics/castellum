from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('subjects', '0059_consent_excluded_by_us'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subject',
            options={
                'permissions': [
                    ('export_subject', 'Can export all data related to a subject'),
                    ('view_audit_trail', 'Can view audit trail'),
                    (
                        'add_to_study',
                        'Can add subject to a study without checking filters',
                    ),
                    ('list_participations', 'Can list all study participations'),
                ],
                'verbose_name': 'Subject',
            },
        ),
    ]
