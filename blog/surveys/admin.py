from django.contrib import admin

from surveys.models import Survey, SurveyTag, SurveyRadio, SurveyView, SurveyVote


admin.site.register(Survey)
admin.site.register(SurveyTag)
admin.site.register(SurveyRadio)
admin.site.register(SurveyView)
admin.site.register(SurveyVote)