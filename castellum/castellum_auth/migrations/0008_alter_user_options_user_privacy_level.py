from django.db import migrations, models


def migrate_data(apps, schema_editor):
    User = apps.get_model('castellum_auth', 'User')
    User.objects.filter(user_permissions__codename='privacy_level_1').update(privacy_level=1)
    User.objects.filter(user_permissions__codename='privacy_level_2').update(privacy_level=2)


class Migration(migrations.Migration):
    dependencies = [
        ("castellum_auth", "0007_user_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="privacy_level",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "0 (regular)"), (1, "1 (increased)"), (2, "2 (high)")],
                default=0,
                verbose_name="Privacy level",
            ),
        ),
        migrations.RunPython(migrate_data),
        migrations.AlterModelOptions(
            name="user",
            options={"ordering": ["username"]},
        ),
    ]
