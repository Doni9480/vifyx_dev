# Generated by Django 5.0.6 on 2024-08-15 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0005_alter_draftalbumphoto_draft_album'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='description',
            field=models.TextField(default=1, verbose_name='Description'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='draftalbum',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
    ]
