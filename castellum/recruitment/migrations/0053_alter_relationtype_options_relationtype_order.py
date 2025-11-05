from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('recruitment', '0052_relationtype_relation_relationtypetranslation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='relationtype',
            options={'ordering': ['order'], 'verbose_name': 'Relation type', 'verbose_name_plural': 'Relation types'},
        ),
        migrations.AddField(
            model_name='relationtype',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
