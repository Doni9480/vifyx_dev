# Generated by Django 5.0.6 on 2024-07-22 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0008_survey_namespace'),
    ]

    operations = [
        migrations.AlterField(
            model_name='draftsurvey',
            name='language',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Language'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='language',
            field=models.CharField(max_length=255, verbose_name='Language'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='namespace',
            field=models.CharField(default='posts', verbose_name='Namespace'),
        ),
    ]
