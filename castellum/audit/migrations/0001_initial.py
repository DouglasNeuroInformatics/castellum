from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='AuditEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(max_length=32)),
                ('username', models.CharField(max_length=150)),
                ('study_pk', models.BigIntegerField(null=True)),
                ('subject_pk', models.UUIDField(null=True)),
                ('extra', models.JSONField(null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
