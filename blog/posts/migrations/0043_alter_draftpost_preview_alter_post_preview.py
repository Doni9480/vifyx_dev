# Generated by Django 5.0.6 on 2024-09-09 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0042_remove_post_likes_postlike'),
    ]

    operations = [
        migrations.AlterField(
            model_name='draftpost',
            name='preview',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/posts/drafts/previews', verbose_name='Preview'),
        ),
        migrations.AlterField(
            model_name='post',
            name='preview',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/posts/previews', verbose_name='Preview'),
        ),
    ]
