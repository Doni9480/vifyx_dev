# Generated by Django 5.0.6 on 2024-09-10 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0043_alter_draftpost_preview_alter_post_preview'),
    ]

    operations = [
        migrations.AddField(
            model_name='draftpost',
            name='size',
            field=models.IntegerField(null=True, verbose_name='Size preview (KB)'),
        ),
        migrations.AddField(
            model_name='post',
            name='size',
            field=models.IntegerField(null=True, verbose_name='Size preview (KB)'),
        ),
    ]
