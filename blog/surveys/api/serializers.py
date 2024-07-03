import json
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from surveys.models import Survey, DraftSurvey, SurveyTag, SurveyRadio
from notifications.models import NotificationSurvey
from users.models import Follow


class SurveySerializer(serializers.ModelSerializer):
    tags = serializers.CharField(required=False, write_only=True)
    answers = serializers.CharField(required=False, write_only=True)
    edit_answers = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Survey
        fields = (
            "preview",
            "title",
            "description",
            "content",
            "language",
            "tags",
            "answers",
            "edit_answers",
            "blog",
            "level_access",
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

        answers = attrs.get("answers", False)
        edit_answers = attrs.get("edit_answers", False)
        if not answers and not edit_answers:
            raise serializers.ValidationError(
                {"answers": "This fields may not be blank."}
            )

        self.answers = []
        self.edit_answers = {}

        if answers:
            self.answers = answers.split(",")
            # if '' in answers
            self.answers = [value for value in self.answers if value]
            if len(self.answers) > 10:
                raise serializers.ValidationError(
                    {"answers": "There should be no more than 10 answer options."}
                )
            del attrs["answers"]

        if edit_answers:
            self.edit_answers = json.loads(edit_answers)
            del attrs["edit_answers"]

        return attrs

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

        if self.edit_answers:
            answers_survey = SurveyRadio.objects.filter(survey=survey)
            for answer_survey in answers_survey:
                if not str(answer_survey.id) in self.edit_answers.keys():
                    answer_survey.delete()
                else:
                    answer_survey.title = self.edit_answers[str(answer_survey.id)]
                    answer_survey.save()

        if self.answers:
            for answer in self.answers:
                SurveyRadio.objects.create(title=answer, survey=survey)

        if (
            not self._instance and survey.level_access < 2
        ):  # if this not edit to survey and survey is free
            follows = Follow.objects.filter(user=self.user)
            for follow in follows:
                if follow.follower.is_notificated:
                    NotificationSurvey.objects.create(
                        survey=survey, user=follow.follower
                    )

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


# draft survey
class DraftSurveySerializer(serializers.ModelSerializer):
    tags = serializers.CharField(required=False, write_only=True)
    answers = serializers.CharField(required=False, write_only=True)
    edit_answers = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = DraftSurvey
        fields = (
            "preview",
            "title",
            "description",
            "content",
            "tags",
            "answers",
            "edit_answers",
            "blog",
            "level_access",
        )

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

        answers = attrs.get("answers", False)
        edit_answers = attrs.get("edit_answers", False)

        if not answers and not edit_answers:
            raise serializers.ValidationError(
                {"answers": "This fields may not be blank."}
            )

        self.answers = []
        self.edit_answers = {}

        if answers:
            self.answers = answers.split(",")
            # if '' in answers
            self.answers = [value for value in self.answers if value]
            if len(self.answers) > 10:
                raise serializers.ValidationError(
                    {"answers": "There should be no more than 10 answer options."}
                )
            del attrs["answers"]

        if edit_answers:
            self.edit_answers = json.loads(edit_answers)
            del attrs["edit_answers"]

        return attrs

    def save(self):
        draft_survey = super(DraftSurveySerializer, self).save()

        # if this edit to draft
        old_tags = SurveyTag.objects.filter(draft_survey=draft_survey)
        for old_tag in old_tags:
            if not old_tag in self.tags:
                old_tag.delete()

        if self.tags:
            for tag in self.tags:
                SurveyTag.objects.create(draft_survey=draft_survey, title=tag)

        if self.edit_answers:
            draft_answers_survey = SurveyRadio.objects.filter(draft_survey=draft_survey)
            for draft_answer_survey in draft_answers_survey:
                print(draft_answer_survey.id, self.edit_answers)
                if not str(draft_answer_survey.id) in self.edit_answers.keys():
                    draft_answer_survey.delete()
                else:
                    draft_answer_survey.title = self.edit_answers[
                        str(draft_answer_survey.id)
                    ]
                    draft_answer_survey.save()

        if self.answers:
            for answer in self.answers:
                SurveyRadio.objects.create(title=answer, draft_survey=draft_survey)

        return draft_survey
