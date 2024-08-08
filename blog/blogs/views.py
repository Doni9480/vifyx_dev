from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.http import Http404

from blogs.models import Blog, LevelAccess, PaidFollow, Donate
from blogs.forms import BlogForm
from blogs.utils import get_filter_kwargs, get_blog_list, get_views_period, get_users_period

from posts.models import Post, PostTag
from posts.utils import get_views_and_comments_to_posts

from surveys.models import Survey, SurveyRadio, SurveyTag
from surveys.utils import get_views_and_comments_to_surveys

from custom_tests.models import Test
from custom_tests.utils import get_views_and_comments_to_tests

from quests.models import Quest
from quests.utils import get_views_and_comments_to_quests

from notifications.models import NotificationBlog

from blog.translations import main_dict

from itertools import chain
from operator import attrgetter


def main(request):    
    filter_kwargs = get_filter_kwargs(request)
    q = request.GET.get('q')
    if q == 'tracked':
        notification_blogs = NotificationBlog.objects.filter(follower=request.user.id)
        blog_list = []
        for notification_blog in notification_blogs:
            filter_kwargs['blog'] = notification_blog.blog
            blog_list += get_blog_list(filter_kwargs)
    else:
        blog_list = get_blog_list(filter_kwargs)
    
    paginator = Paginator(blog_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    popular_day, popular_week = get_views_period(filter_kwargs)
    users_day, users_week = get_users_period()
    
    data = {
        "page_obj": page_obj,
        "popular_day": popular_day,
        "popular_week": popular_week,
        "users_day": users_day,
        "users_week": users_week,
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }
    data = dict(
        list(data.items()) + list(main_dict[request.user.language].items())
    )

    return render(request, "blogs/main.html", data)

def popular(request):
    filter_kwargs = get_filter_kwargs(request)
    query = get_views_period(filter_kwargs, full=True)
    q = request.GET.get('q')
    if q == 'week':
        title = 'Popular of the week'
        paginator = Paginator(query[1], 5)
    else:
        q = 'day'
        title = 'Popular of the day'
        paginator = Paginator(query[0], 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "blogs/popular.html", {'page_obj': page_obj, 'title': title, 'q': q})

def popular_users(request):
    query = get_users_period(full=True)
    q = request.GET.get('q')
    if q == 'week':
        title = 'Popular users of the week'
        paginator = Paginator(query[1], 5)
    else:
        q = 'day'
        title = 'Popular users of the day'
        paginator = Paginator(query[0], 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "blogs/popular_users.html", {'page_obj': page_obj, 'title': title, 'q': q})

@login_required(login_url="/registration/login")
def create(request):
    return render(
        request,
        "blogs/create.html",
        {"recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY},
    )

def show(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    level_follows = LevelAccess.objects.filter(blog=blog)
    
    filter_kwargs = get_filter_kwargs(request)
    filter_kwargs['blog'] = blog

    posts = get_views_and_comments_to_posts(Post.objects.filter(**filter_kwargs))
    surveys = get_views_and_comments_to_surveys(Survey.objects.filter(**filter_kwargs))
    tests = get_views_and_comments_to_tests(Test.objects_show.filter(**filter_kwargs))
    quests = get_views_and_comments_to_quests(Quest.objects.filter(**filter_kwargs))
    blog_list = sorted(chain(posts, surveys, tests, quests), key=attrgetter("date"), reverse=True)

    paid_follow = PaidFollow.objects.filter(follower=request.user.id, blog=blog)
    if paid_follow:
        paid_follow = paid_follow.first()
    else:
        paid_follow = None

    paginator = Paginator(blog_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    get_notifications_blog_filter = NotificationBlog.objects.filter(follower=request.user.id, blog=blog)
    if get_notifications_blog_filter:
        get_notifications_blog = get_notifications_blog_filter.first()
    else:
        get_notifications_blog = None

    data = {
        "blog": blog,
        "page_obj": page_obj,
        "paid_follow": paid_follow,
        "get_notifications_blog": get_notifications_blog,
        "level_follows": level_follows,
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }

    return render(request, "blogs/show.html", data)

def best_blogs(request):
    blog_models = Blog.objects.all()
    for blog in blog_models:
        blog.scores = 0
        
        for post in Post.objects.filter(blog=blog):
            blog.scores += post.scores
        for survey in Survey.objects.filter(blog=blog):
            scores = 0
            options = SurveyRadio.objects.filter(survey=survey)
            for option in options:
                scores += option.scores
            blog.scores += scores
            
    blogs = sorted(chain(blog_models), key=attrgetter("scores"), reverse=True)[:5]
    return render(request, "blogs/popular_blogs.html", {"blogs": blogs})

@login_required(login_url="/registration/login")
def donate(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if blog.user == request.user:
        raise Http404()
    
    return render(request, 'blogs/donate.html', {"recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY, 'blog_id': blog.pk})

@login_required(login_url="/registration/login")
def donate_show(request, id):
    donate = get_object_or_404(Donate, id=id)
    if request.user != donate.blog.user:
        raise Http404()
    return render(request, 'blogs/donate_show.html', {'donate': donate})
    
def edit(request, slug):
    instance = get_object_or_404(Blog, user=request.user.id, slug=slug)

    form = BlogForm(instance=instance)

    data = {
        "form": form,
        "blog_id": instance.id,
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }

    return render(request, "blogs/edit.html", data)

@login_required(login_url="/registration/login")
def create_level_follow(request, slug):
    blog = get_object_or_404(Blog, slug=slug, user=request.user, is_private=True)
    
    level = 1
    level_follows = LevelAccess.objects.filter(blog=blog)
    if level_follows:
        level = level_follows.order_by('-level').first().level + 1
    
    return render(request, 'blogs/create_level_follow.html', {
        "blog": blog, 
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        "level": level,
    })
    
def search(request, q):
    filter_kwargs = get_filter_kwargs(request)
    
    posts = get_views_and_comments_to_posts(Post.level_access_objects.filter(title__icontains=q, **filter_kwargs))
    surveys = get_views_and_comments_to_surveys(Survey.level_access_objects.filter(title__icontains=q, **filter_kwargs))
    tests = get_views_and_comments_to_tests(Test.level_access_objects.filter(title__icontains=q, **filter_kwargs))
    quests = get_views_and_comments_to_quests(Quest.level_access_objects.filter(title__icontains=q, **filter_kwargs))
    
    blog_list = sorted(chain(posts, surveys, tests, quests), key=attrgetter("date"), reverse=True)
    
    paginator = Paginator(blog_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blogs/search.html', {'page_obj': page_obj, 'q': q})

def search_tags(request, q):
    filter_kwargs = get_filter_kwargs(request)
    post_tags = PostTag.objects.filter(title=q)
    posts = []
    for tag in post_tags:
        try:
            posts.append(get_object_or_404(Post.level_access_objects, id=tag.post.pk, **filter_kwargs))
        except Http404 as e:
            pass
    survey_tags = SurveyTag.objects.filter(title=q)
    surveys = []
    for tag in survey_tags:
        try:
            surveys.append(get_object_or_404(Survey.level_access_objects, id=tag.survey.pk))
        except Http404 as e:
            pass
            
    blog_list = sorted(chain(posts, surveys), key=attrgetter("date"), reverse=True)
    
    paginator = Paginator(blog_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blogs/search_tags.html', {'page_obj': page_obj, 'q': q})