# Generated by Django 5.0.6 on 2024-09-10 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0011_alter_album_preview_alter_albumphoto_photo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='size',
            field=models.IntegerField(null=True, verbose_name='Size preview (KB)'),
        ),
        migrations.AddField(
            model_name='albumphoto',
            name='size',
            field=models.IntegerField(null=True, verbose_name='Size photo (KB)'),
        ),
        migrations.AddField(
            model_name='draftalbum',
            name='size',
            field=models.IntegerField(null=True, verbose_name='Size preview (KB)'),
        ),
        migrations.AddField(
            model_name='draftalbumphoto',
            name='size',
            field=models.IntegerField(null=True, verbose_name='Size photo (KB)'),
        ),
    ]
