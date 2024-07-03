from rest_framework import serializers

from posts.models import Post
from surveys.models import Survey


class NotificationPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'preview',
            'title',
            'slug',
            'date'
        )


class NotificationSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = (
            'preview',
            'title',
            'slug',
            'date'
        )
        

class NotificationPostShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'preview',
            'title',
            'slug',
            'date',
            'user'
        )


class NotificationSurveyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = (
            'preview',
            'title',
            'slug',
            'date',
            'user'
        )