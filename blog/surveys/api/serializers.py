import json

from rest_framework import serializers

from surveys.models import Survey, DraftSurvey, SurveyTag, SurveyRadio, DraftSurveyRadio, DraftSurveyTag
from notifications.models import Notification, NotificationBlog

from blog.validators import check_language

from blogs.models import LevelAccess, BlogFollow

from django.shortcuts import get_object_or_404
from django.http import Http404


class AnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    
    class Meta:
        model = SurveyRadio
        fields = [
            "id",
            "title",
        ]


class SurveySerializer(serializers.ModelSerializer):
    tags = serializers.CharField(required=False, write_only=True)
    answers_set = AnswerSerializer(source="answers", many=True)
    language = serializers.CharField(validators=[check_language])
    level_access = serializers.IntegerField()

    class Meta:
        model = Survey
        fields = [
            "preview",
            "title",
            "description",
            "content",
            "language",
            "tags",
            "blog",
            "answers_set",
            "level_access",
        ]

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
        self._instance = kwargs.get("instance", False)
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

        if attrs.get("blog") and self._instance:
            del attrs["blog"]

        return attrs
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        
        if validated_data.get('level_access', None) and validated_data['level_access'] > 0:
            validated_data['level_access'] = get_object_or_404(
                LevelAccess, level=validated_data['level_access'], blog=validated_data['blog']
            )
        try:
            if not (validated_data.get('level_access', None).__class__.__name__ == 'LevelAccess'):
                del validated_data['level_access']
        except KeyError as e:
            pass
        
        survey = Survey(**validated_data)
        survey.user = self.user
        survey.save()
        for answer_data in answers_data:
            answer_data['survey'] = survey
            SurveyRadio.objects.create(**answer_data)

        return survey
    
    def update(self, survey, validated_data):
        answers_data = validated_data.pop('answers')
        
        for attr, value in validated_data.items():
            setattr(survey, attr, value)
        survey.save()
        
        ids = []
        for answer_data in answers_data:
            if answer_data.get('id', False):
                ids.append(answer_data['id'])
                answer = get_object_or_404(SurveyRadio, id=answer_data['id'])
                if answer.survey.user == self.user:
                    answer.title = answer_data['title']
                    answer.save()
            else:
                answer_data['survey'] = survey
                option = SurveyRadio.objects.create(**answer_data)
                ids.append(option.id)
        
        options = SurveyRadio.objects.filter(survey=survey)
        for option in options:
            if option.id not in ids and option.survey.user == self.user:
                option.delete()

        return survey

    def save(self):
        survey = super(SurveySerializer, self).save()

        # if this edit to survey
        old_tags = SurveyTag.objects.filter(survey=survey)
        for old_tag in old_tags:
            if not old_tag in self.tags:
                old_tag.delete()

        if self.tags:
            for tag in self.tags:
                SurveyTag.objects.create(survey=survey, title=tag)

        if (
            not self._instance and not survey.level_access
        ):  # if this not edit to survey and survey is free
            follows = BlogFollow.objects.filter(blog=survey.blog)
            for follow in follows:
                if follow.follower.is_notificated:
                    if NotificationBlog.objects.filter(
                        follower=follow.follower, blog=survey.blog, user=survey.user, get_notifications_blog=True
                    ):
                        Notification.objects.create(survey=survey, user=follow.follower)

        return survey


class SurveyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = (
            "id",
            "preview",
            "title",
            "description",
            "content",
            "language",
            "user",
            "date",
        )


class SurveyIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = (
            "id",
            "slug",
            "preview",
            "title",
            "description",
            "content",
            "language",
            "user",
            "date",
        )


class SurveyScoresSerializer(serializers.Serializer):
    scores = serializers.IntegerField()


class TermSerializer(serializers.Serializer):
    term = serializers.IntegerField()


class SurveyNoneSerializer(serializers.Serializer):
    pass


class DraftAnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    
    class Meta:
        model = DraftSurveyRadio
        fields = (
            "id",
            "title",
        )


# draft survey
class DraftSurveySerializer(serializers.ModelSerializer):
    tags = serializers.CharField(required=False, write_only=True)
    answers_set = DraftAnswerSerializer(source="answers", many=True, required=False)
    language = serializers.CharField(required=False, validators=[check_language])
    level_access = serializers.IntegerField(required=False)

    class Meta:
        model = DraftSurvey
        fields = (
            "preview",
            "title",
            "description",
            "content",
            "language",
            "tags",
            "blog",
            "answers_set",
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
            
        draft_survey = DraftSurvey(**validated_data)
        draft_survey.user = self.user
        draft_survey.save()
        for answer_data in answers_data:
            answer_data['draft_survey'] = draft_survey
            DraftSurveyRadio.objects.create(**answer_data)
    
        return draft_survey
    
    def update(self, draft_survey, validated_data):
        answers_data = validated_data.get("answers", [])
        if answers_data:
            del validated_data['answers']
        
        for attr, value in validated_data.items():
            if attr == 'level_access':
                if value <= 0:
                    value = None
                else:
                    value = get_object_or_404(
                        LevelAccess, level=value, blog=draft_survey.blog
                    )
            setattr(draft_survey, attr, value)
        draft_survey.save()
        
        ids = []
        for answer_data in answers_data:
            if answer_data.get('id', False):
                ids.append(answer_data['id'])
                answer = get_object_or_404(DraftSurveyRadio, id=answer_data['id'])
                if answer.draft_survey.user == self.user:
                    answer.title = answer_data['title']
                    answer.save()
            else:
                answer_data['draft_survey'] = draft_survey
                option = DraftSurveyRadio.objects.create(**answer_data)
                ids.append(option.id)
        
        options = DraftSurveyRadio.objects.filter(draft_survey=draft_survey)
        for option in options:
            if option.id not in ids and option.draft_survey.user == self.user:
                option.delete()

        return draft_survey

    def save(self):
        draft_survey = super(DraftSurveySerializer, self).save()

        # if this edit to draft
        old_tags = DraftSurveyTag.objects.filter(draft_survey=draft_survey)
        for old_tag in old_tags:
            if not old_tag in self.tags:
                old_tag.delete()

        if self.tags:
            for tag in self.tags:
                DraftSurveyTag.objects.create(draft_survey=draft_survey, title=tag)

        return draft_survey
    
