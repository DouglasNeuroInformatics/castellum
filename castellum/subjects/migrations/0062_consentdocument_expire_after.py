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
    ]
