from django.urls import path

from surveys.views import create, edit, show, index, draft_survey_create


urlpatterns = [
    path('', index, name="index"),
    path('blog/<slug:slug>/create/', create, name='create'),
    path('edit/<slug:slug>/', edit, name="edit"),
    path('show/<slug:slug>/', show, name="show"),
    
    # draft
    path('blog/<slug:slug>/create/', draft_survey_create, name="draft_survey_create"),
]
