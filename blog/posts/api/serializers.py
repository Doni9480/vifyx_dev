from rest_framework import serializers
from posts.models import DraftPost as DraftModel, DraftPostTag as DraftTag
from posts.models import Post, PostTag
from users.models import Follow
from notifications.models import NotificationPost


class TagMixin(serializers.ModelSerializer):
    tags = serializers.CharField(required=False, write_only=True)

    def validate_tags(self, tags):
        print(tags)
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


class DraftSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = DraftModel
        fields = (
            "preview",
            "title",
            "description",
            "content",
            "blog",
            "tags",
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

        return attrs

    def save(self):
        draft = super(DraftSerializer, self).save()

        # if this edit to draft
        old_tags = DraftTag.objects.filter(draft=draft)
        for old_tag in old_tags:
            if not old_tag in self.tags:
                old_tag.delete()

        for tag in self.tags:
            DraftTag.objects.create(draft=draft, title=tag)

        return draft


class PostSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Post
        fields = (
            "preview",
            "title",
            "description",
            "content",
            "language",
            "blog",
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

        return attrs

    def save(self):
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
            not self._instance and post.level_access < 2
        ):  # if this not edit to survey and post is free
            follows = Follow.objects.filter(user=self.user)
            for follow in follows:
                if follow.follower.is_notificated:
                    NotificationPost.objects.create(post=post, user=follow.follower)

        return post


class PostShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
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


class PostIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
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


class PostScoresSerializer(serializers.Serializer):
    scores = serializers.IntegerField()


class TermSerializer(serializers.Serializer):
    term = serializers.IntegerField()


class PostNoneSerializer(serializers.Serializer):
    pass
