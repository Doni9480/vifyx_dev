# Generated by Django 5.0.6 on 2024-07-09 16:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_draftpost_add_survey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(default=datetime.datetime(2024, 7, 9, 16, 9, 55, 210394, tzinfo=datetime.timezone.utc), verbose_name='Content'),
            preserve_default=False,
        ),
    ]
