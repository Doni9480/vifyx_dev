# Generated by Django 5.0.6 on 2024-08-19 22:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0009_albumtag'),
    ]

    operations = [
        migrations.CreateModel(
            name='DraftAlbumTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('draft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='albums.draftalbum', verbose_name='Draft')),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
    ]
