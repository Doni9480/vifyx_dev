# Generated by Django 5.0.6 on 2024-08-05 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0031_alter_draftpost_category_alter_draftpost_subcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='postview',
            name='day',
            field=models.IntegerField(default=0, verbose_name='Day view'),
        ),
        migrations.AddField(
            model_name='postview',
            name='week',
            field=models.IntegerField(default=0, verbose_name='Week view'),
        ),
    ]
