# Generated by Django 5.0.6 on 2024-08-19 18:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_tests', '0021_test_likes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='likes',
        ),
        migrations.CreateModel(
            name='TestLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_like', to='custom_tests.test', verbose_name='Test')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_test_like', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
