from django import forms

from django_summernote import fields

from quests.models import Quest, QuestionQuest, QuestionQuestAnswer


class QuestForm(forms.ModelForm):
    content = fields.SummernoteTextFormField(required=False)

    class Meta:
        model = Quest
        fields = (
            "preview",
            "title",
            "description",
            "content",
            "timer",
        )


class QuestionForm(forms.ModelForm):
    class Meta:
        model = QuestionQuest
        fields = (
            "text",
        )


class QuestionAnswerForm(forms.ModelForm):
    class Meta:
        model = QuestionQuestAnswer
        fields = (
            "text",
        )
