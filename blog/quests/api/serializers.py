from rest_framework import serializers
from quests.models import Quest, QuestionQuest, QuestionQuestAnswer


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
    answer_set = QuestionQuestAnswerDetailSerializer(source="answers", many=True, read_only=False)
    children = RecursiveQuestion(many=True, required=False)

    class Meta:
        model = QuestionQuest
        fields = (
            "id",
            "text",
            "quest",
            "children",
            "answer_set",
        )

    def create(self, validated_data):
        answers_data = validated_data.pop('answer_set')
        question = QuestionQuest.objects.create(**validated_data)
        for answer_data in answers_data:
            QuestionQuestAnswer.objects.create(question=question, **answer_data)
        return question

    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answer_set')
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


class QuestSerializer(serializers.ModelSerializer):
    timer = serializers.IntegerField(
        help_text="Таймер (опционально). Пример: 10 (в минутах)",
        required=False,
        default=0,
    )
    slug = serializers.CharField(
        help_text="Можете оставить пустым так как есть автогенерация на основе 'title'.(Опционально)",
        required=False,
    )
    preview = serializers.FileField()

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
            "timer",
        )


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
        
        
