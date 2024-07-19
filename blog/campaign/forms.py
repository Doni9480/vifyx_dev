from django.forms import ModelForm
from .models import Campaign, Task

class CampaignForm(ModelForm):
    class Meta:
        model = Campaign
        fields = "__all__"

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = "__all__"