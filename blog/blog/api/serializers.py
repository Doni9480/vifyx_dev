from rest_framework import serializers

from posts.models import Post

from surveys.models import Survey


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
            "scores",
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
