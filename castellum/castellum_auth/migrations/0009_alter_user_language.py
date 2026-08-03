from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('castellum_auth', '0001_squashed_0008_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='language',
            field=models.CharField(blank=True, max_length=5, verbose_name='Language'),
        ),
    ]
