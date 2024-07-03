from django import forms
from django_summernote.widgets import SummernoteWidget
from django_summernote import fields

from surveys.models import Survey, DraftSurvey


class SurveyForm(forms.ModelForm):
    content = fields.SummernoteTextFormField(required=False)

    class Meta:
        model = Survey
        fields = (
            "preview",
            "title",
            "description",
            "content",
        )


# draft
class DraftSurveyForm(forms.ModelForm):
    content = forms.CharField(
        widget=SummernoteWidget(attrs={"summernote": {"width": "100%"}}), required=False
    )

    class Meta:
        model = DraftSurvey
        fields = (
            "preview",
            "title",
            "description",
            "content",
        )
