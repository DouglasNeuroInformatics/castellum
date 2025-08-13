import django.db.models.deletion
import parler.fields
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('studies', '0001_initial'),
        ('recruitment', '0001_initial'),
        ('subjects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectfiltergroup',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studies.study'),
        ),
        migrations.AddField(
            model_name='subjectfilter',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruitment.attribute'),
        ),
        migrations.AddField(
            model_name='subjectfilter',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruitment.subjectfiltergroup'),
        ),
        migrations.AddField(
            model_name='reliabilityentry',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studies.study', verbose_name='Study'),
        ),
        migrations.AddField(
            model_name='reliabilityentry',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject', verbose_name='Subject'),
        ),
        migrations.AddField(
            model_name='participationconsent',
            name='participation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruitment.participation'),
        ),
        migrations.AddField(
            model_name='participation',
            name='assigned_recruiter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='studies.studymembership', verbose_name='Assigned recruiter'),
        ),
        migrations.AddField(
            model_name='participation',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='recruitment.mailbatch', verbose_name='Mail batch'),
        ),
        migrations.AddField(
            model_name='participation',
            name='execution_tags',
            field=models.ManyToManyField(blank=True, to='recruitment.executiontag', verbose_name='Execution tags'),
        ),
        migrations.AddField(
            model_name='participation',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studies.study', verbose_name='Study'),
        ),
        migrations.AddField(
            model_name='participation',
            name='subject',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='subjects.subject'),
        ),
        migrations.AddField(
            model_name='newsmailbatch',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studies.study', verbose_name='Study'),
        ),
        migrations.AddField(
            model_name='mailbatch',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studies.study', verbose_name='Study'),
        ),
        migrations.AddField(
            model_name='executiontag',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studies.study'),
        ),
        migrations.AddField(
            model_name='attributetranslation',
            name='master',
            field=parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='recruitment.attribute'),
        ),
        migrations.AddField(
            model_name='attributechoicetranslation',
            name='master',
            field=parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='recruitment.attributechoice'),
        ),
        migrations.AddField(
            model_name='attributechoice',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruitment.attribute'),
        ),
        migrations.AddField(
            model_name='attributecategorytranslation',
            name='master',
            field=parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='recruitment.attributecategory'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='recruitment.attributecategory'),
        ),
        migrations.AlterUniqueTogether(
            name='participation',
            unique_together={('study', 'subject')},
        ),
        migrations.AlterUniqueTogether(
            name='attributetranslation',
            unique_together={('language_code', 'master')},
        ),
        migrations.AlterUniqueTogether(
            name='attributechoicetranslation',
            unique_together={('language_code', 'master')},
        ),
        migrations.AlterUniqueTogether(
            name='attributecategorytranslation',
            unique_together={('language_code', 'master')},
        ),
    ]
