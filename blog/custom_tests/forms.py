from django import forms

from django_summernote import fields

from custom_tests.models import Test, Question, QuestionAnswer


class TestForm(forms.ModelForm):
    content = fields.SummernoteTextFormField(required=False)

    class Meta:
        model = Test
        fields = (
            "preview",
            "title",
            "description",
            "content",
            "timer",
        )


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = (
            "question",
        )


class QuestionAnswerForm(forms.ModelForm):
    class Meta:
        model = QuestionAnswer
        fields = (
            "variant",
            "is_true",
        )