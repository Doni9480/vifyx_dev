# Generated by Django 5.0.6 on 2024-07-16 04:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0007_task_content_usage_type_task_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='type',
            new_name='task_type',
        ),
    ]
