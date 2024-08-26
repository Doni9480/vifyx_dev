"""
URL configuration for blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from blog.views import redirect_main
from blog.admin import login, logout

from blogs.views import best_blogs, search, search_tags, main, popular, popular_users

from scheduler.scheduler import TasksScheduler

from .swagger import urlpatterns as urlpatterns_swagger

urlpatterns = [
    # path('admin/login/', login),
    # path('admin/logout/', logout),
    path('admin/', admin.site.urls),

    path('', redirect_main, name="redirect_main"),
    path('main/', main, name="main"),
    path('popular/', popular, name="popular"),
    path('popular_users/', popular_users, name="popular_users"),
    path('best_blogs/', best_blogs, name="best_blogs"),
    path('search/<str:q>/', search, name="search"),
    path('search_tags/<str:q>/', search_tags, name="search_tags"),

    path('', include(('users.urls', 'users'), namespace="users")),
    path('blogs/', include(('blogs.urls', 'blogs'), namespace="blogs")),
    path('posts/', include(('posts.urls', 'posts'), namespace="posts")),
    # path('drafts/', include(('drafts.urls', 'drafts'), namespace="drafts")),
    # path('drafts_survey/', include(('drafts_survey.urls', 'drafts_survey'), namespace="drafts_survey")),
    path('surveys/', include(('surveys.urls', 'surveys'), namespace="surveys")),
    path('notifications/', include(('notifications.urls', 'notifications'), namespace="notifications")),
    path('albums/', include(('albums.urls', 'albums'), namespace="albums")),
    path('tests/', include('custom_tests.urls')),
    path('quests/', include('quests.urls')),
    path('companies/', include('campaign.urls')),
    path('periodic_bonuses/', include('periodic_bonuses.urls')),
    path('contests/', include(('contests.urls', 'contests'), namespace="contests")),

    path('summernote/', include('django_summernote.urls')),
    path('api/v1/blogs/', include('blogs.api.urls')),
    path('api/v1/users/', include('users.api.urls')),
    path('api/v1/posts/', include('posts.api.urls')),
    path('api/v1/surveys/', include('surveys.api.urls')),
    # # path('api/v1/drafts/', include('drafts.api.urls')),
    # # path('api/v1/drafts_survey/', include('drafts_survey.api.urls')),
    path('api/v1/comments/', include('comments.api.urls')),
    path('api/v1/notifications/', include('notifications.api.urls')),
    path('api/v1/tests/', include('custom_tests.api.urls')),
    path('api/v1/quests/', include('quests.api.urls')),
    path('api/v1/companies/', include('campaign.api.urls')),
    path('api/v1/periodic_bonuses/', include('periodic_bonuses.api.urls')),
    path('api/v1/albums/', include('albums.api.urls')),
    path('api/v1/contests/', include('contests.api.urls')),
    
    # path('language/<str:language>/', language, name="language"),

    *urlpatterns_swagger
]

# running scheduler
try:
    scheduler = TasksScheduler()
    scheduler.run()
except Exception as e:
    print(f"Scheduler error: {e}")

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)