import argparse
from rest_framework import serializers
from campaign.models import Campaign, Task, UserTaskChecking


class CampaignSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    slug = serializers.CharField(
        help_text="Можете оставить пустым так как есть автогенерация на основе 'name'.(Опционально)",
        required=False,
    )
    
    class Meta:
        model = Campaign
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "prize_fund",
            "image",
            "user",
            "created_at",
        )


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    
    class Meta:
        model = Task
        fields = "__all__"


class UserTaskCheckingSerializer(serializers.ModelSerializer):
    task = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)
    points_awarded = serializers.CharField(read_only=True)
    end_date = serializers.CharField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)

    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop("user", 1)
    #     self.task = kwargs.pop("task", 1)

    #     super().__init__(self, *args, **kwargs)

    # def save(self, **kwargs):
    #     if not self.instance:
    #         self.validated_data["user"] = self.user
    #         self.validated_data["task"] = self.task
    #     obj = super().save(**kwargs)
    #     print(obj)
    #     return obj

    class Meta:
        model = UserTaskChecking
        fields = [
            "id",
            "task",
            "user",
            "is_completed",
            "points_awarded",
            "start_date",
            "end_date",
        ]
