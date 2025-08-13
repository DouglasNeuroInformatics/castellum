import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('studies', '0001_initial'),
        ('recruitment', '0001_initial'),
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='assigned_conductors',
            field=models.ManyToManyField(blank=True, related_name='+', to='studies.studymembership', verbose_name='Assigned conductors'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='participation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruitment.participation', verbose_name='Participation'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studies.studysession', verbose_name='Session'),
        ),
        migrations.AlterUniqueTogether(
            name='appointment',
            unique_together={('session', 'participation')},
        ),
    ]
