# Generated by Django 5.0.6 on 2024-07-26 18:23

import django.db.models.manager
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_tests', '0009_test_hidden'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='test',
            managers=[
                ('objects_for_post', django.db.models.manager.Manager()),
            ],
        ),
    ]
