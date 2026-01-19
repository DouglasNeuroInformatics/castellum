from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('subjects', '0061_alter_consent_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='consentdocument',
            name='expire_after',
            field=models.DurationField(blank=True, null=True, verbose_name='Expire after'),
        ),
        migrations.AddField(
            model_name='consent',
            name='expire_at_notified',
            field=models.BooleanField(default=False, verbose_name='Expiration notification sent'),
        ),
    ]
