# Generated by Django 5.0.6 on 2024-07-21 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0007_alter_draftsurvey_level_access_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='namespace',
            field=models.CharField(default='surveys', verbose_name='Namespace'),
        ),
    ]
