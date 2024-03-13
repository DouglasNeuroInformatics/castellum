from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("subjects", "0053_alter_report_subject"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="subject",
            options={
                "permissions": [
                    ("export_subject", "Can export all data related to a subject"),
                    ("view_audit_trail", "Can view audit trail"),
                ],
                "verbose_name": "Subject",
            },
        ),
    ]
