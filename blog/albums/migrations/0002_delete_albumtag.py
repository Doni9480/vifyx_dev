# Generated by Django 5.0.6 on 2024-08-12 19:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AlbumTag',
        ),
    ]
