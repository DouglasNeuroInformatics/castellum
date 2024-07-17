from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recruitment", "0048_alter_attribute_id_alter_attributecategory_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="participation",
            name="status",
            field=models.IntegerField(
                choices=[
                    (0, "not contacted"),
                    (1, "not reached"),
                    (4, "follow-up scheduled"),
                    (5, "awaiting response"),
                    (10, "recruitment mail sent"),
                    (3, "participating"),
                    (7, "participating (dropped out)"),
                    (2, "excluded"),
                    (6, "excluded (dropped out)"),
                    (8, "excluded by cleanup"),
                    (9, "completed"),
                ],
                default=0,
                verbose_name="Status of participation",
            ),
        ),
    ]
