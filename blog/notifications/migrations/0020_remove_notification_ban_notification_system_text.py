# Generated by Django 5.0.6 on 2024-09-04 18:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0019_remove_notification_system_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='ban',
        ),
        migrations.AddField(
            model_name='notification',
            name='system_text',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='notifications.systemtext'),
        ),
    ]
