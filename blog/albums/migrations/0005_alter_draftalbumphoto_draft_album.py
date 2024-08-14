# Generated by Django 5.0.6 on 2024-08-13 23:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0004_draftalbum_draftalbumphoto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='draftalbumphoto',
            name='draft_album',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='albums.draftalbum', verbose_name='Draft album'),
        ),
    ]
