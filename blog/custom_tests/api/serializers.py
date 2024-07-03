from rest_framework import serializers
# from drf_extra_fields.fields import Base64ImageField
from custom_tests.models import Test, Question, QuestionAnswer


class QuestionAnswerSerializer(serializers.ModelSerializer):
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
            "test",
            "answers_set",
        )

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = Question(**validated_data)
        question.save()
        for answer_data in answers_data:
            answer_data['question'] = question
            QuestionAnswer.objects.create(**answer_data)
        return question

    def update(self, instance, validated_data):
        question_obj = Question.objects.filter(id=instance.id)[0]
        question_obj.question = validated_data.get("question", instance.question)
        question_obj.save()
        return question_obj


class TestSerializer(serializers.ModelSerializer):
    timer = serializers.IntegerField(
        help_text="Таймер (опционально). Пример: 10 (в минутах)", required=False
    )
    slug = serializers.CharField(
        help_text="Можете оставить пустым так как есть автогенерация на основе 'title'.(Опционально)"
    )
    preview = serializers.FileField(help_text="img", required=False)
    scores = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Test
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
        )


class TestDetailSerializer(serializers.ModelSerializer):
    preview = serializers.FileField(help_text="img", required=False)
    question_set = QuestionSerializer(source="questions", many=True)

    class Meta:
        model = Test
        fields = (
            "id",
            "preview",
            "title",
            "description",
            "content",
            "user",
            "language",
            "scores",
            "slug",
            "question_set",
        )



class TestEditSerializer(serializers.ModelSerializer):
    preview = serializers.FileField(required=False)

    class Meta:
        model = Test
        fields = (
            "id",
            "preview",
            "title",
            "description",
            "content",
            "user",
            "language",
            "scores",
            "slug",
        )


class TestVisibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = (
            "id",
            "hide_to_user",
            "hide_to_moderator",
        )
