import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('recruitment', '0051_parler'),
        ('subjects', '0061_alter_consent_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=16, unique=True)),
                ('reverse_key', models.CharField(max_length=16, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('other', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reverse_relation_set', related_query_name='reverse_relation', to='subjects.subject', verbose_name='Other person')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruitment.relationtype', verbose_name='Type of relation')),
            ],
        ),
        migrations.CreateModel(
            name='RelationTypeTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('label', models.CharField(max_length=64)),
                ('reverse_label', models.CharField(max_length=64)),
                ('parent', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='recruitment.relationtype')),
            ],
            options={
                'unique_together': {('language_code', 'parent')},
            },
        ),
    ]
