# Generated by Django 5.0.6 on 2024-07-21 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_tests', '0006_test_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='namespace',
            field=models.CharField(default='tests', verbose_name='Namespace'),
        ),
    ]
