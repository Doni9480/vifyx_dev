# Generated by Django 5.0.6 on 2024-08-21 10:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0005_alter_task_task_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionsCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaigns', models.ManyToManyField(to='campaign.campaign', verbose_name='Campaign')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions_campaigns', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Subscriptions Campaigns',
                'verbose_name_plural': 'Subscriptions Campaigns',
            },
        ),
    ]
