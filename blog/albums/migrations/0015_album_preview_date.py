# Generated by Django 5.0.6 on 2024-09-11 22:01

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0014_alter_album_preview_alter_albumphoto_photo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='preview_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
