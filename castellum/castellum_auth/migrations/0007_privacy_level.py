from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('castellum_auth', '0006_remove_user_general_domains'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivacyLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(verbose_name='Value')),
                ('label', models.CharField(max_length=64, verbose_name='Label')),
            ],
        ),
    ]
