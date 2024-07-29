from django import forms
from django_summernote.widgets import SummernoteWidget
from django_summernote import fields

from posts.models import Post, DraftPost


class PostForm(forms.ModelForm):
    content = fields.SummernoteTextFormField(required=False)

    class Meta:
        model = Post
        fields = (
            "preview",
            "title",
            "content",
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
