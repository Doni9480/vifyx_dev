# Generated by Django 5.0.6 on 2024-09-01 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_merge_20240901_1848'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_banned',
            field=models.BooleanField(default=False, verbose_name='Is banned'),
        ),
    ]
