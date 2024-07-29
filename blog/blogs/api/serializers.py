from rest_framework import serializers

from posts.models import Post

from surveys.models import Survey

from quests.models import Quest

from custom_tests.models import Test

from blogs.models import Blog, LevelAccess, Donate

from notifications.models import Notification


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = (
            "preview",
            "title",
            'description',
            'slug',
            "is_private",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self._instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        is_private = attrs.get("is_private")

        if is_private and Blog.objects.filter(is_private=is_private, user=self.user):
            raise serializers.ValidationError(
                {"is_private": "You can create only one private blog."}
            )
            
        if self._instance and attrs.get('slug'):
            del attrs['slug']
            
        return attrs
    

class BlogShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = (
            'id',
            'preview',
            'title',
            'description',
            'user',
            'is_private',
            'date',
        )


class PaySerializer(serializers.Serializer):
    term = serializers.IntegerField()
    level = serializers.IntegerField()
    

class DonateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Donate
        fields = (
            'amount',
            'message',
            'blog',
        )
        
    def save(self):
        donate = super(DonateSerializer, self).save()
        
        user = donate.blog.user
        if user.is_notificated:
            Notification.objects.create(donate=donate, user=user)
            
        return donate
    

class DonateShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donate
        fields = (
            'message',
            'amount',
            'user',
            'date'
        )


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "preview",
            "title",
            "slug",
            "date",
            "user",
            "level_access",
        )


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = (
            "id",
            "preview",
            "title",
            "slug",
            "date",
            "user",
            "level_access",
        )
        

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = (
            "id",
            "preview",
            "title",
            "slug",
            "date",
            "user",
            "level_access",
        )
        

class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = (
            "id",
            "preview",
            "title",
            "slug",
            "date",
            "user",
            "level_access",
        )


class LevelFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelAccess
        fields = (
            'preview',
            'title',
            'description',
            'scores',
            'blog',
        )
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        
    def validate(self, attrs):
        attrs['level'] = 1
        level_follows = LevelAccess.objects.filter(blog=attrs['blog'])
        if level_follows:
            level_access = level_follows.order_by('-level').first()
            if level_access.scores > attrs['scores']:
                raise serializers.ValidationError({'scores': 'This level should be more expensive than the previous one.'})
            attrs['level'] = level_access.level + 1
            
        return attrs