# Generated by Django 5.0.6 on 2024-07-09 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_alter_post_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='language',
            field=models.CharField(verbose_name='Language'),
        ),
    ]
