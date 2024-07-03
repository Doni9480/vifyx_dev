from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import HttpResponseRedirect

from notifications.models import NotificationPost, NotificationSurvey

from itertools import chain

from operator import attrgetter


@login_required(login_url='/registration/login')
def index(request):
    notification_posts = NotificationPost.objects.filter(user=request.user.id)
    notification_surveys = NotificationSurvey.objects.filter(user=request.user.id)
    
    posts = []
    for post in notification_posts:
        post.post.namespace = 'posts'
        posts.append(post.post)

    surveys = []
    for survey in notification_surveys:
        survey.survey.namespace = 'surveys'
        surveys.append(survey.survey)

    notification_blogs = sorted(chain(posts, surveys), key=attrgetter('date'), reverse=True)
    paginator = Paginator(notification_blogs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'notifications/index.html', {'page_obj': page_obj})