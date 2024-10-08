# Generated by Django 5.0.6 on 2024-08-07 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_tests', '0019_alter_test_namespace'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='category',
        ),
        migrations.RemoveField(
            model_name='subcategory',
            name='subcategory',
        ),
        migrations.AddField(
            model_name='category',
            name='category_eng',
            field=models.CharField(default=1, verbose_name='Category eng'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='category_rus',
            field=models.CharField(default=1, verbose_name='Category rus'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subcategory',
            name='subcategory_eng',
            field=models.CharField(default=1, verbose_name='Subcategory eng'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subcategory',
            name='subcategory_rus',
            field=models.CharField(default=1, verbose_name='Subcategory rus'),
            preserve_default=False,
        ),
    ]
