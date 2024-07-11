from django import forms
from django_summernote.widgets import SummernoteWidget
from django_summernote import fields

from posts.models import Post, DraftPost, Question, QuestionAnswer


class PostForm(forms.ModelForm):
    content = fields.SummernoteTextFormField(required=False)

    class Meta:
        model = Post
        fields = (
            "preview",
            "title",
            "content",
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


class DraftForm(forms.ModelForm):
    content = forms.CharField(
        widget=SummernoteWidget(attrs={"summernote": {"width": "100%"}}), required=False
    )

    class Meta:
        model = DraftPost
        fields = (
            "preview",
            "title",
            "content",
            "blog",
        )
