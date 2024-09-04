from rest_framework import serializers
from notifications.models import Notification, Ban, Unban, ExpiringFollow, SystemText, AnswerNotification
from posts.models import Post
from surveys.models import Survey
from quests.models import Quest
from albums.models import Album
from custom_tests.models import Test
from contests.models import Contest
from blogs.models import Donate
from comments.models import Answer


class NotificationPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'id',
            'preview',
            'title',
            'slug',
            'namespace'
        )


class NotificationSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = (
            'id',
            'preview',
            'title',
            'slug',
            'namespace'
        )
        

class NotificationTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = (
            'id',
            'preview',
            'title',
            'slug',
            'namespace'
        )
        

class NotificationQuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = (
            'id',
            'preview',
            'title',
            'slug',
            'namespace'
        )
        
        
class NotificationAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = (
            'id',
            'preview',
            'title',
            'slug',
            'namespace'
        )
        

class NotificationContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = (
            'id',
            'preview',
            'title',
            'slug',
            'start_date',
            'end_date',
        )
        

class NotificationBanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ban
        fields = (
            'id',
            'text',
        )
        

class NotificationUnbanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unban
        fields = (
            'id',
            'text',
        )
        

class NotificationExpiringFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiringFollow
        fields = (
            'id',
            'text',
        )


class NotificationDonateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donate
        fields = (
            'id',
            'message',
        )
        
        
class NotificationSystemTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemText
        fields = (
            'id',
            'english',
            'russian',
            'title_rus',
            'title_eng',
            'text_rus',
            'text_eng',
        )
        
        
class NotificationAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerNotification
        fields = (
            'answer',
            'namespace',
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