from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.http import Http404

from blogs.models import Blog, LevelAccess, PaidFollow, Donate
from blogs.forms import BlogForm

from posts.models import Post
from posts.utils import get_views_and_comments_to_posts

from surveys.models import Survey, SurveyRadio
from surveys.utils import get_views_and_comments_to_surveys

from notifications.models import NotificationBlog

from itertools import chain
from operator import attrgetter


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
    
    filter_kwargs = {'hide_to_user': False, 'hide_to_moderator': False, 'language': request.user.language}
    if request.user.language == 'any':
        del filter_kwargs['language']
    if request.user.is_staff:
        del filter_kwargs['hide_to_moderator']
        del filter_kwargs['hide_to_user']

    posts = get_views_and_comments_to_posts(Post.objects.filter(**filter_kwargs))
    surveys = get_views_and_comments_to_surveys(Survey.objects.filter(**filter_kwargs))
    blog_list = sorted(chain(posts, surveys), key=attrgetter("date"), reverse=True)

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
    return render(request, "popular.html", {"blogs": blogs})

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