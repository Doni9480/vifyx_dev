# Generated by Django 5.0.6 on 2024-07-09 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.CharField(default='any', verbose_name='Language'),
        ),
    ]
