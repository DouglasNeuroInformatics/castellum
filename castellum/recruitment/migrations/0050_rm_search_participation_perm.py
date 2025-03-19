from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('recruitment', '0049_alter_participation_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='participation',
            options={'permissions': [('conduct_study', 'Can conduct studies'), ('recruit', 'Can recruit')], 'verbose_name': 'Study participation', 'verbose_name_plural': 'Study participations'},
        ),
    ]
