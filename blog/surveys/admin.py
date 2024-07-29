from django.contrib import admin

from surveys.models import Survey, SurveyTag, SurveyRadio, SurveyView, SurveyVote, Category, Subcategory


admin.site.register(Survey)
admin.site.register(SurveyTag)
admin.site.register(SurveyRadio)
admin.site.register(SurveyView)
admin.site.register(SurveyVote)
admin.site.register(Category)
admin.site.register(Subcategory)