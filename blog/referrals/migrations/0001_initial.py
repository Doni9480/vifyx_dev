# Generated by Django 5.0.6 on 2024-08-02 16:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, verbose_name='Code')),
                ('tasks_completed', models.IntegerField(default=0, verbose_name='Task Completed')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('referral_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referred', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Referral',
                'verbose_name_plural': 'Referrals',
            },
        ),
    ]
