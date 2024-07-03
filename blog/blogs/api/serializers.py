from rest_framework import serializers

from posts.models import Post

from surveys.models import Survey

from blogs.models import Blog, LevelAccess


class BlogSerializer(serializers.ModelSerializer):
    level_two = serializers.IntegerField(required=False)
    level_three = serializers.IntegerField(required=False)
    level_four = serializers.IntegerField(required=False)

    class Meta:
        model = Blog
        fields = (
            "preview",
            "title",
            "is_private",
            "level_two",
            "level_three",
            "level_four",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", 1)
        self._instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        is_private = attrs.get("is_private")

        if is_private and Blog.objects.filter(is_private=is_private, user=self.user):
            raise serializers.ValidationError(
                {"is_private": "You can create only one private blog."}
            )

        self.level_two = attrs.get("level_two")
        self.level_three = attrs.get("level_three")
        self.level_four = attrs.get("level_four")

        if not is_private and (self.level_two or self.level_three or self.level_four):
            raise serializers.ValidationError(
                {"is_private": "For access levels, you need to select a private blog."}
            )

        is_validation_errors = {}
        message = "Must not be less than zero."
        if self.level_two and self.level_two < 0:
            is_validation_errors["level_two"] = message
        if self.level_three and self.level_three < 0:
            is_validation_errors["level_three"] = message
        if self.level_four and self.level_four < 0:
            is_validation_errors["level_four"] = message

        if is_validation_errors:
            raise serializers.ValidationError(is_validation_errors)

        if self.level_two:
            del attrs["level_two"]
        if self.level_three:
            del attrs["level_three"]
        if self.level_four:
            del attrs["level_four"]

        return attrs

    def save(self):
        blog = super(BlogSerializer, self).save()

        if blog.is_private and not self._instance:
            LevelAccess.objects.create(level=1, scores=0, blog=blog)
            LevelAccess.objects.create(level=2, scores=self.level_two, blog=blog)
            LevelAccess.objects.create(level=3, scores=self.level_three, blog=blog)
            LevelAccess.objects.create(level=4, scores=self.level_four, blog=blog)

        return blog


class PaySerializer(serializers.Serializer):
    term = serializers.IntegerField()


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
