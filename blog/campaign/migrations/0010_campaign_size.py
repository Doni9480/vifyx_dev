# Generated by Django 5.0.6 on 2024-09-10 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0009_alter_campaign_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='size',
            field=models.IntegerField(null=True, verbose_name='Size preview (KB)'),
        ),
    ]
