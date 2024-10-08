# Generated by Django 5.0.6 on 2024-08-03 19:42

import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_user_referral_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='referral_code',
            field=models.CharField(blank=True, default=users.models.gen_referral_code, null=True, unique=True, verbose_name='Referral code'),
        ),
    ]
