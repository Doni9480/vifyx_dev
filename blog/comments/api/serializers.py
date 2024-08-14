from rest_framework import serializers

from comments.models import Comment, Answer


class CommentTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "text",
            "test",
        )


class CommentQuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "text",
            "quest",
        )


class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "text",
            "post",
        )


class CommentSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "text",
            "survey",
        )
        

class CommentAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "text",
            "album",
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("text",)


class CommentPostShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "date",
            "post",
            "user",
            "delete_from_user",
        )


class CommentSurveyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "date",
            "survey",
            "user",
            "delete_from_user",
        )


class CommentTestShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "date",
            "test",
            "user",
            "delete_from_user",
        )


class CommentQuestShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "date",
            "quest",
            "user",
            "delete_from_user",
        )
        

class CommentAlbumShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "date",
            "album",
            "user",
            "delete_from_user",
        )


class CommentFullSerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=True)
    post = serializers.IntegerField(
        required=False, help_text="Укажите ID поста или оставите пустым"
    )
    survey = serializers.IntegerField(
        required=False, help_text="Укажите ID опроса или оставите пустым"
    )
    test = serializers.IntegerField(
        required=False, help_text="Укажите ID теста или оставите пустым"
    )
    quest = serializers.IntegerField(
        required=False, help_text="Укажите ID квеста или оставите пустым"
    )

    class Meta:
        model = Comment
        fields = ("text", "post", "survey", "test", "quest")


class AnswerPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            "text",
            "post",
            "comment",
        )


class AnswerSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            "text",
            "survey",
            "comment",
        )


class AnswerTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            "text",
            "test",
            "comment",
        )


class AnswerQuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            "text",
            "quest",
            "comment",
        )
        

class AnswerAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            "text",
            "album",
            "comment",
        )


class AnswerPostShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            "id",
            "text",
            "date",
            "post",
            "user",
            "comment",
        )


class AnswerSurveyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            "id",
            "text",
            "date",
            "survey",
            "user",
            "comment",
        )


class AnswerTestShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            "id",
            "text",
            "date",
            "test",
            "user",
            "comment",
        )


class AnswerQuestShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            "id",
            "text",
            "date",
            "quest",
            "user",
            "comment",
        )
        

class AnswerAlbumShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            "id",
            "text",
            "date",
            "album",
            "user",
            "comment",
        )


class AnswerFullSerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=True)
    post = serializers.IntegerField(
        required=False, help_text="Укажите ID поста или оставите пустым"
    )
    survey = serializers.IntegerField(
        required=False, help_text="Укажите ID опроса или оставите пустым"
    )
    test = serializers.IntegerField(
        required=False, help_text="Укажите ID теста или оставите пустым"
    )
    quest = serializers.IntegerField(
        required=False, help_text="Укажите ID квеста или оставите пустым"
    )
    album = serializers.IntegerField(
        required=False, help_text="Укажите ID альбома или оставите пустым"
    )
    comment = serializers.IntegerField(
        required=False, help_text="Укажите ID комментария или оставите пустым"
    )
    class Meta:
        model = Answer
        fields = ("text", "post", "survey", "test", "quest", "album", "comment")
        