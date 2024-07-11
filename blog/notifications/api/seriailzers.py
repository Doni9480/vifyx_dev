from rest_framework import serializers

from notifications.models import Notification

from posts.models import Post

from surveys.models import Survey

from blogs.models import Donate


class NotificationPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'id',
            'preview',
            'title',
            'slug',
            'date'
        )


class NotificationSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = (
            'id',
            'preview',
            'title',
            'slug',
            'date'
        )


class NotificationDonateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donate
        fields = (
            'id',
            'message',
            'date',
        )
        

class NotificationPostShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'id',
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
            'id',
            'preview',
            'title',
            'slug',
            'date',
            'user'
        )
        

class NotificationDonateShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donate
        fields = (
            'id',
            'amount',
            'blog',
            'message',
            'user',
            'date',
        )
        

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            'id',
            'post',
            'donate',
            'survey',
            'user',
        )
        
        
class NotificationNoneSerializer(serializers.Serializer):
    pass