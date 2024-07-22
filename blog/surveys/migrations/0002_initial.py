# Generated by Django 5.0.6 on 2024-07-03 19:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blogs', '0002_initial'),
        ('surveys', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='draftsurvey',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='draftsurveyradio',
            name='draft_survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.draftsurvey', verbose_name='Draft survey'),
        ),
        migrations.AddField(
            model_name='draftsurveytag',
            name='draft_survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.draftsurvey', verbose_name='Draft survey'),
        ),
        migrations.AddField(
            model_name='survey',
            name='blog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blogs.blog'),
        ),
        migrations.AddField(
            model_name='survey',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='surveyradio',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.survey', verbose_name='Survey'),
        ),
        migrations.AddField(
            model_name='surveytag',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.survey', verbose_name='Survey'),
        ),
        migrations.AddField(
            model_name='surveyview',
            name='survey',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='surveys.survey', verbose_name='Survey'),
        ),
        migrations.AddField(
            model_name='surveyview',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='User', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='surveyvote',
            name='option',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='surveys.surveyradio', verbose_name='Option'),
        ),
        migrations.AddField(
            model_name='surveyvote',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.survey', verbose_name='Survey'),
        ),
        migrations.AddField(
            model_name='surveyvote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
