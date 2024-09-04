from rest_framework import serializers
from quests.models import Quest, QuestionQuest, QuestionQuestAnswer, Subcategory, QuestTag
from blog.validators import check_language
from blogs.models import LevelAccess
from notifications.models import Notification, NotificationBlog
from blogs.models import BlogFollow


class RecursiveQuestion(serializers.Serializer):

    def to_representation(self, value):
        if self.parent:
            serializer = self.parent.parent.__class__(value, context=self.context)
            return serializer.data
        return None


class QuestionQuestAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionQuestAnswer
        fields = (
            "id",
            "text",
            "result",
            "next_question"
        )


class QuestionQuestAnswerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionQuestAnswer
        fields = (
            "id",
            "text",
            "result",
            "question",
            "next_question",
        )


class QuestionQuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionQuest
        fields = (
            "id",
            "parent",
        )


class QuestionQuestDetailSerializer(serializers.ModelSerializer):
    answers_set = QuestionQuestAnswerDetailSerializer(source="answers", many=True, read_only=False)
    children = RecursiveQuestion(many=True, required=False)

    class Meta:
        model = QuestionQuest
        fields = (
            "id",
            "text",
            "quest",
            "children",
            "answers_set",
        )

    def create(self, validated_data):
        answers_data = validated_data.pop('answers_set')
        question = QuestionQuest.objects.create(**validated_data)
        for answer_data in answers_data:
            QuestionQuestAnswer.objects.create(question=question, **answer_data)
        return question

    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers_set')
        instance.text = validated_data.get('text', instance.text)
        instance.save()

        keep_answers = []
        for answer_data in answers_data:
            if "id" in answer_data.keys():
                if QuestionQuestAnswer.objects.filter(id=answer_data["id"]).exists():
                    answer = QuestionQuestAnswer.objects.get(id=answer_data["id"])
                    answer.text = answer_data.get('text', answer.text)
                    answer.save()
                    keep_answers.append(answer.id)
                else:
                    continue
            else:
                answer = QuestionQuestAnswer.objects.create(question=instance, **answer_data)
                keep_answers.append(answer.id)

        # Remove books that are not in the keep_books list
        for answer in instance.answers.all():
            if answer.id not in keep_answers:
                answer.delete()
        return instance


class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionQuest
        fields = (
            "id",
            "question",
        )


class QuestionDetailSerializer(serializers.ModelSerializer):
    answers = QuestionQuestAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuestionQuest
        fields = (
            "id",
            "question",
            "quest",
            "answers",
        )
        
        
class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = (
            "id",
            "subcategory_rus",
            "subcategory_eng",
        )


class QuestSerializer(serializers.ModelSerializer):
    timer = serializers.IntegerField(
        help_text="Таймер (опционально). Пример: 10 (в минутах)",
        required=False,
        default=0,
    )
    preview = serializers.FileField()
    language = serializers.CharField(validators=[check_language])
    tags = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Quest
        fields = (
            "id",
            "title",
            "language",
            "description",
            "content",
            "preview",
            "user",
            "blog",
            "category",
            "subcategory",
            "level_access",
            "tags",
            "timer",
        )
        
    def __init__(self, *args, **kwargs):
        self._instance = kwargs.get("instance")
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
        
        level_access = attrs.get('level_access')
        if level_access:
            if self.instance:
                blog = self.instance.blog
            else:
                blog = attrs['blog']
            if not LevelAccess.objects.filter(id=level_access.pk, blog=blog):
                raise serializers.ValidationError({'level_access': 'Invalid level access.'})
        return attrs
    
    def update(self, quest, validated_data):        
        for attr, value in validated_data.items():
            setattr(quest, attr, value)
        if not validated_data.get('level_access'):
            quest.level_access = None
        quest.save()
        
        return quest
    
    def save(self):
        quest = super(QuestSerializer, self).save()
        
        # if this edit to quest
        old_tags = QuestTag.objects.filter(quest=quest)
        for old_tag in old_tags:
            if not old_tag in self.tags:
                old_tag.delete()

        if self.tags:
            for tag in self.tags:
                QuestTag.objects.create(quest=quest, title=tag)
        
        if (
            not self.instance and not quest.level_access
        ):
            follows = BlogFollow.objects.filter(blog=quest.blog)
            for follow in follows:
                if follow.follower.is_notificated:
                    if NotificationBlog.objects.filter(
                        follower=follow.follower, blog=quest.blog, user=quest.user, get_notifications_blog=True, get_notifications_quest=True,
                    ):
                        Notification.objects.create(quest=quest, user=follow.follower)
                        
        return quest


class QuestDetailSerializer(serializers.ModelSerializer):
    timer = serializers.IntegerField(
        help_text="Таймер (опционально). Пример: 10 (в минутах)",
        required=False,
    )
    slug = serializers.CharField(
        help_text="Можете оставить пустым так как есть автогенерация на основе 'title'.(Опционально)",
        required=False,
    )
    questions = QuestionQuestDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Quest
        fields = (
            "id",
            "title",
            "slug",
            "language",
            "description",
            "content",
            "preview",
            "user",
            "scores",
            "timer",
            "questions",
        )


class QuestVisibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = (
            "id",
            "hide_to_user",
            "hide_to_moderator",
        )
        
        
