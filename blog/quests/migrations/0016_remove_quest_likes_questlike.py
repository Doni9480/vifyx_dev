# Generated by Django 5.0.6 on 2024-08-19 18:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quests', '0015_quest_likes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quest',
            name='likes',
        ),
        migrations.CreateModel(
            name='QuestLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quest', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='quest_like', to='quests.quest', verbose_name='Quest')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_quest_like', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
