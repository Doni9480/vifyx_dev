# Generated by Django 5.0.6 on 2024-09-10 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quests', '0019_quest_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quest',
            name='size',
            field=models.IntegerField(blank=True, null=True, verbose_name='Size preview (KB)'),
        ),
    ]
