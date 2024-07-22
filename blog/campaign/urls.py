# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('campaign/new/', campaign_create, name='campaign_create'),
    path('campaign/<str:slug>/', CampaignDetailView.as_view(), name='campaign_detail'),
    path('campaign/<str:slug>/edit/', campaign_update, name='campaign_update'),
    path('campaign/<str:slug>/task/new/', task_create, name='task_create'),
    path('campaign/<str:slug>/task/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('campaign/<str:slug>/task/<int:pk>/edit/', task_update, name='task_update'),
]
