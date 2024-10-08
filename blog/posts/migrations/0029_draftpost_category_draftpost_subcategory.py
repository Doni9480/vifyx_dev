# Generated by Django 5.0.6 on 2024-07-29 17:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0028_category_alter_post_category_subcategory_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='draftpost',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='posts.category', verbose_name='Category'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='draftpost',
            name='subcategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.subcategory', verbose_name='Subcategory'),
        ),
    ]
