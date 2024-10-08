# Generated by Django 5.0.6 on 2024-08-21 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0003_remove_contest_album_remove_contest_post_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contest',
            options={'verbose_name': 'Contest', 'verbose_name_plural': 'Contests'},
        ),
        migrations.AddField(
            model_name='contest',
            name='slug',
            field=models.SlugField(default=1, max_length=255, unique=True, verbose_name='URL'),
            preserve_default=False,
        ),
    ]
