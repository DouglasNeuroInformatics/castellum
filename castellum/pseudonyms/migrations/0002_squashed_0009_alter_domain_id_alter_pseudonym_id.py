import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subjects', '0001_squashed_0059_consent_excluded_by_us'),
        ('pseudonyms', '0001_squashed_initial'),
        ('recruitment', '0022_squashed_0049_alter_participation_status'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='pseudonym',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='subjects.subject'),
        ),
        migrations.AddField(
            model_name='domain',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='domain',
            name='exportable_attributes',
            field=models.ManyToManyField(blank=True, related_name='+', to='recruitment.attribute', verbose_name='Exportable recruitment attributes'),
        ),
        migrations.AddField(
            model_name='domain',
            name='managers',
            field=models.ManyToManyField(blank=True, related_name='general_domains', to=settings.AUTH_USER_MODEL, verbose_name='Users who can access this pseudonym list'),
        ),
        migrations.AlterUniqueTogether(
            name='pseudonym',
            unique_together={('domain', 'subject'), ('domain', 'pseudonym')},
        ),
    ]
