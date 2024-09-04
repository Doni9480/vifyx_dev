from rest_framework import serializers
from posts.models import DraftPost as DraftModel, DraftPostTag as DraftTag
from posts.models import Post, PostTag, PostRadio, DraftPostRadio, Subcategory
from posts.api.utils import create_test
from notifications.models import Notification, NotificationBlog
from blogs.models import LevelAccess, BlogFollow

from blog.validators import check_language

from django.shortcuts import get_object_or_404


class TagMixin(serializers.ModelSerializer):
    tags = serializers.CharField(required=False, write_only=True)

    def validate_tags(self, tags):
        # tag_list = tags.split(',')
        tag_list = [value for value in tags if value]  # Remove empty tags
        return tag_list

    def save_tags(self, instance, tag_model):
        # Delete old tags
        tag_model.objects.filter(**{self.tag_field: instance}).delete()
        # Create new tags
        for tag in self.tags:
            tag_model.objects.create(**{self.tag_field: instance}, title=tag)

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        if self.tags:
            self.save_tags(instance, self.tag_model)
        return instance


class DraftAnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    
    class Meta:
        model = DraftPostRadio
        fields = (
            "id",
            "title",
        )


class DraftSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(required=False, write_only=True)
    answers_set = DraftAnswerSerializer(required=False, many=True, source="answers")
    language = serializers.CharField(required=False, validators=[check_language])

    class Meta:
        model = DraftModel
        fields = (
            "preview",
            "title",
            "content",
            "blog",
            "answers_set",
            "language",
            "category",
            "subcategory",
            "add_survey",
            "is_paid",
            "amount",
            "tags",
            "is_create_test",
            "level_access",
        )
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", 1)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        tags = attrs.get("tags")

        self.tags = []
        if tags:
            del attrs["tags"]
            self.tags = tags.split(",")
            # if '' in tags
            self.tags = [value for value in self.tags if value]

        level_access = attrs.get('level_access')
        if level_access:
            if not LevelAccess.objects.filter(id=level_access.pk, blog=attrs['blog']):
                raise serializers.ValidationError({'level_access': 'Invalid level access.'})
        
        if not attrs.get('is_paid', False):
            if attrs.get('amount', False):
                del attrs['amount']
                
        if not attrs.get('amount', False):
            attrs['is_paid'] = False
            
        if not attrs.get('add_survey', False) and attrs.get('answers', None):
            raise serializers.ValidationError({'add_survey': "for options, you need to check the box."})
        if attrs.get('add_survey', False) and not attrs.get('answers', None):
            raise serializers.ValidationError({'answers_set': "This field is required."})
        return attrs
    
    def create(self, validated_data):
        answers_data = validated_data.get("answers", [])
        if answers_data:
            del validated_data['answers']
        
        draft_post = DraftModel(**validated_data)
        draft_post.user = self.user
        draft_post.save()
        for answer_data in answers_data:
            answer_data['draft_post'] = draft_post
            DraftPostRadio.objects.create(**answer_data)
    
        return draft_post
    
    def update(self, draft_post, validated_data):
        answers_data = validated_data.get("answers", [])
        if answers_data:
            del validated_data['answers']
            
        for attr, value in validated_data.items():
            setattr(draft_post, attr, value)
            
        if not validated_data.get('level_access'):
            draft_post.level_access = None
            
        draft_post.add_survey = validated_data.get('add_survey', False)
        if not validated_data.get('subcategory'):
            draft_post.subcategory = None
        draft_post.save()
        
        ids = []
        for answer_data in answers_data:
            if answer_data.get('id', False):
                ids.append(answer_data['id'])
                answer = get_object_or_404(DraftPostRadio, id=answer_data['id'])
                if answer.draft_post.user == self.user:
                    answer.title = answer_data['title']
                    answer.save()
            else:
                answer_data['draft_post'] = draft_post
                option = DraftPostRadio.objects.create(**answer_data)
                ids.append(option.id)
        
        options = DraftPostRadio.objects.filter(draft_post=draft_post)
        for option in options:
            if option.id not in ids and option.draft_post.user == self.user:
                option.delete()
        return draft_post

    def save(self):
        draft = super(DraftSerializer, self).save()
        if not draft.is_paid and draft.amount:
            draft.amount = None
            draft.save()

        # if this edit to draft
        old_tags = DraftTag.objects.filter(draft=draft)
        for old_tag in old_tags:
            if not old_tag in self.tags:
                old_tag.delete()

        for tag in self.tags:
            DraftTag.objects.create(draft=draft, title=tag)

        return draft
    

class PostAnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    
    class Meta:
        model = PostRadio
        fields = [
            'id',
            'title',
        ]
        

class PostSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(required=False, write_only=True)
    answers_set = PostAnswerSerializer(source="answers", many=True, required=False)
    language = serializers.CharField(validators=[check_language])
    is_create_test = serializers.BooleanField(required=False, write_only=True)
    
    class Meta:
        model = Post
        fields = (
            "preview",
            "title",
            "content",
            "answers_set",
            "language",
            "category",
            "subcategory",
            "blog",
            "is_paid",
            "add_survey",
            "amount",
            "level_access",
            "is_create_test",
            "tags",
        )

        extra_kwargs = {
            "preview": {"error_messages": {"invalid": "The image may not be blank."}}
        }
        extra_kwargs = {
            "language": {
                "error_messages": {"invalid_choice": "You have not chosen a language."}
            }
        }
        extra_kwargs = {
            "level_access": {
                "error_messages": {
                    "invalid_choice": "You have not chosen a level access."
                }
            }
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", 1)
        self._instance = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        try:
            if self._instance:
                if attrs.get('category') and not attrs.get('subcategory'):
                    raise Exception()
            subcategory = attrs['subcategory']
            category = attrs['category']
            if subcategory.category != category:
                raise Exception()
        except Exception:
            raise serializers.ValidationError({"subcategory": "Invalid subcategory."})
        
        tags = attrs.get("tags")

        self.tags = []
        if tags:
            del attrs["tags"]
            self.tags = tags.split(",")
            # if '' in tags
            self.tags = [value for value in self.tags if value]

        if attrs.get("blog") and self._instance:
            del attrs["blog"]
            
        level_access = attrs.get('level_access')
        if level_access:
            if self._instance:
                blog = self._instance.blog
            else:
                blog = attrs['blog']
            if not LevelAccess.objects.filter(id=level_access.pk, blog=blog):
                raise serializers.ValidationError({'level_access': 'Invalid level access.'})
            
        if attrs.get('is_paid', False) and not attrs.get('amount', False):
            raise serializers.ValidationError({
                "amount": "This field is not may blank."
            })
            
        if not attrs.get('is_paid', False):
            if attrs.get('amount', False):
                del attrs['amount']
                
        if not attrs.get('add_survey', False) and attrs.get('answers', None):
            raise serializers.ValidationError({'add_survey': "for options, you need to check the box."})
        if attrs.get('add_survey', False) and not attrs.get('answers', None):
            raise serializers.ValidationError({'answers_set': "This field is required."})
        
        self.create_test = attrs.get('is_create_test')
        if self.create_test != None:
            del attrs['is_create_test']
            
        return attrs
    
    def create(self, validated_data):
        answers_data = validated_data.get("answers", [])
        if answers_data:
            del validated_data['answers']
            
        post = Post(**validated_data)
        post.user = self.user
        post.save()
        for answer_data in answers_data:
            answer_data['post'] = post
            PostRadio.objects.create(**answer_data)
        
        return post
    
    def update(self, post, validated_data):
        answers_data = validated_data.get("answers", [])
        if answers_data:
            del validated_data['answers']
        
        for attr, value in validated_data.items():
            setattr(post, attr, value)
        
        if not validated_data.get('level_access'):
            post.level_access = None
        post.add_survey = validated_data.get('add_survey', False)
        post.save()
        
        ids = []
        for answer_data in answers_data:
            if answer_data.get('id', False):
                ids.append(answer_data['id'])
                answer = get_object_or_404(PostRadio, id=answer_data['id'])
                if answer.post.user == self.user:
                    answer.title = answer_data['title']
                    answer.save()
            else:
                answer_data['post'] = post
                option = PostRadio.objects.create(**answer_data)
                ids.append(option.id)
        
        options = PostRadio.objects.filter(post=post)
        for option in options:
            if option.id not in ids and option.post.user == self.user:
                option.delete()

        return post
    
    def save(self):
        if self._instance:
            self.amount = self._instance.amount
            self.is_paid = self._instance.is_paid
            
        post = super(PostSerializer, self).save()

        # if this edit to post
        old_tags = PostTag.objects.filter(post=post)
        for old_tag in old_tags:
            if not old_tag in self.tags:
                old_tag.delete()

        if self.tags:
            for tag in self.tags:
                PostTag.objects.create(post=post, title=tag)

        if (
            not self._instance and not post.level_access
        ):  # if this not edit to survey and post is free
            follows = BlogFollow.objects.filter(blog=post.blog)
            for follow in follows:
                if follow.follower.is_notificated:
                    if NotificationBlog.objects.filter(
                        follower=follow.follower, blog=post.blog, user=post.user, get_notifications_blog=True, get_notifications_post=True,
                    ):
                        Notification.objects.create(post=post, user=follow.follower)
        # creating test for post
        if self.create_test:    
            test = create_test(post)
            post.test = test
            post.save()
        elif self._instance and self._instance.test:
            test = self._instance.test
            post.test = None
            post.save()
            test.delete()
        
        return post


class PostShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "preview",
            "title",
            "is_paid",
            "amount",
            "content",
            "language",
            "user",
            "date",
        )
        
        
class PostShowNotBuySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "preview",
            "title",
            "is_paid",
            "content",
            "amount",
            "language",
            "user",
            "date",
        )


class PostIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "slug",
            "preview",
            "title",
            "content",
            "language",
            "user",
            "date",
        )
        
        
class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = (
            "id",
            "subcategory_rus",
            "subcategory_eng",
        )


class PostScoresSerializer(serializers.Serializer):
    scores = serializers.IntegerField()


class TermSerializer(serializers.Serializer):
    term = serializers.IntegerField()


class PostNoneSerializer(serializers.Serializer):
    pass
