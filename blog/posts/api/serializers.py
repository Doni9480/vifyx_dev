from rest_framework import serializers
from posts.models import DraftPost as DraftModel, DraftPostTag as DraftTag
from posts.models import Post, PostTag, PostRadio, DraftPostRadio
from posts.models import Question, QuestionAnswer
from notifications.models import Notification, NotificationBlog
from blogs.models import LevelAccess, BlogFollow

from blog.validators import check_language

from django.shortcuts import get_object_or_404

import json


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


class QuestionAnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    
    class Meta:
        model = QuestionAnswer
        fields = (
            "id",
            "variant",
            "is_true",
        )


class QuestionSerializer(serializers.ModelSerializer):
    answers_set = QuestionAnswerSerializer(source="answers", many=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "question",
            "post",
            "answers_set",
        )
        
    def validate(self, attrs):
        not_id = False
        for answer in attrs['answers']:
            if not answer.get('id', False):
                not_id = True
                break
        if self.instance and not_id:
            raise serializers.ValidationError({'error': 'Something went wrong.'})
        
        return attrs

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = Question(**validated_data)
        question.save()
        for answer_data in answers_data:
            answer_data['question'] = question
            QuestionAnswer.objects.create(**answer_data)
        return question

    def update(self, instance, validated_data):
        answers_list = validated_data.pop('answers')
        for answer in answers_list:
            question_answer = get_object_or_404(QuestionAnswer, id=answer['id'])
            question_answer.variant = answer['variant']
            question_answer.is_true = answer['is_true']
            question_answer.save()
        
        question_obj = Question.objects.filter(id=instance.id)[0]
        question_obj.question = validated_data.get("question", instance.question)
        question_obj.save()
        return question_obj
    

class PostTestDetailSerializer(serializers.ModelSerializer):
    preview = serializers.FileField(help_text="img", required=False)
    question_set = QuestionSerializer(source="questions", many=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "preview",
            "title",
            "content",
            "user",
            "language",
            "scores",
            "slug",
            "question_set",
        )
        

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
    level_access = serializers.IntegerField(required=False)

    class Meta:
        model = DraftModel
        fields = (
            "preview",
            "title",
            "content",
            "blog",
            "answers_set",
            "language",
            "add_survey",
            "is_paid",
            "amount",
            "tags",
            "level_access",
        )
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        tags = attrs.get("tags")

        self.tags = []
        if tags:
            del attrs["tags"]
            self.tags = tags.split(",")
            # if '' in tags
            self.tags = [value for value in self.tags if value]

        if attrs.get("level_access", False) and attrs["level_access"] < 1:
            raise serializers.ValidationError(
                {"level_access": "Please select a valid level access"}
            )
        
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
            
        if validated_data.get('level_access', None) and validated_data['level_access'] > 0:
            validated_data['level_access'] = get_object_or_404(
                LevelAccess, level=validated_data['level_access'], blog=validated_data['blog']
            )
        try:
            if not (validated_data.get('level_access', None).__class__.__name__ == 'LevelAccess'):
                del validated_data['level_access']
        except KeyError as e:
            pass
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
            if attr == 'level_access':
                if value <= 0:
                    value = None
                else:
                    value = get_object_or_404(
                        LevelAccess, level=value, blog=draft_post.blog
                    )
            setattr(draft_post, attr, value)
            
        draft_post.add_survey = validated_data.get('add_survey', False)
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
    level_access = serializers.IntegerField(required=False)
    
    class Meta:
        model = Post
        fields = (
            "preview",
            "title",
            "content",
            "answers_set",
            "language",
            "blog",
            "is_paid",
            "add_survey",
            "amount",
            "level_access",
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
        self.user = kwargs.pop("user", None)
        self._instance = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        tags = attrs.get("tags")

        self.tags = []
        if tags:
            del attrs["tags"]
            self.tags = tags.split(",")
            # if '' in tags
            self.tags = [value for value in self.tags if value]

        if attrs.get("blog") and self._instance:
            del attrs["blog"]
            
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
        return attrs
    
    def create(self, validated_data):
        answers_data = validated_data.get("answers", [])
        if answers_data:
            del validated_data['answers']
            
        if validated_data.get('level_access', None) and validated_data['level_access'] > 0:
            validated_data['level_access'] = get_object_or_404(
                LevelAccess, level=validated_data['level_access'], blog=validated_data['blog']
            )
        try:
            if not (validated_data.get('level_access', None).__class__.__name__ == 'LevelAccess'):
                del validated_data['level_access']
        except KeyError as e:
            pass
            
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
                        follower=follow.follower, blog=post.blog, user=post.user, get_notifications_blog=True
                    ):
                        Notification.objects.create(post=post, user=follow.follower)

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


class PostScoresSerializer(serializers.Serializer):
    scores = serializers.IntegerField()


class TermSerializer(serializers.Serializer):
    term = serializers.IntegerField()


class PostNoneSerializer(serializers.Serializer):
    pass
