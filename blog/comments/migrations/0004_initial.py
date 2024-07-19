# Generated by Django 5.0.6 on 2024-07-13 11:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('comments', '0003_initial'),
        ('custom_tests', '0001_initial'),
        ('surveys', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='survey',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='surveys.survey', verbose_name='Survey'),
        ),
        migrations.AddField(
            model_name='answer',
            name='test',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='custom_tests.test', verbose_name='Test'),
        ),
    ]
