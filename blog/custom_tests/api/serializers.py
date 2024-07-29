from rest_framework import serializers
# from drf_extra_fields.fields import Base64ImageField
from custom_tests.models import Test, Question, QuestionAnswer, Subcategory
from blog.validators import check_language
from django.shortcuts import get_object_or_404
from blogs.models import LevelAccess
from notifications.models import Notification, NotificationBlog
from blogs.models import BlogFollow


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
            "test",
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


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = (
            "id",
            "subcategory",
        )


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
            "date",
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
    language = serializers.CharField(validators=[check_language])

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
            "blog",
            "category",
            "subcategory",
            "level_access",
        )
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", 1)
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
        
        level_access = attrs.get('level_access')
        if level_access:
            if self.instance:
                blog = self.instance.blog
            else:
                blog = attrs['blog']
            if not LevelAccess.objects.filter(id=level_access.pk, blog=blog):
                raise serializers.ValidationError({'level_access': 'Invalid level access.'})
        return attrs
    
    def update(self, test, validated_data):        
        for attr, value in validated_data.items():
            setattr(test, attr, value)
        if not validated_data.get('level_access'):
            test.level_access = None
        test.save()
        
        return test
    
    def save(self):
        test = super(TestEditSerializer, self).save()
        
        if (
            not self._instance and not test.level_access
        ):
            follows = BlogFollow.objects.filter(blog=test.blog)
            print(follows)
            for follow in follows:
                if follow.follower.is_notificated:
                    print('????')
                    if NotificationBlog.objects.filter(
                        follower=follow.follower, blog=test.blog, user=test.user, get_notifications_blog=True
                    ):
                        print('?????')
                        Notification.objects.create(test=test, user=follow.follower)
                        
        return test
    

class TestVisibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = (
            "id",
            "hide_to_user",
            "hide_to_moderator",
        )
