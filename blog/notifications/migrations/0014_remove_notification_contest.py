# Generated by Django 5.0.6 on 2024-08-26 17:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0013_notification_contest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='contest',
        ),
    ]
