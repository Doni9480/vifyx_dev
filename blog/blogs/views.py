from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator

from blogs.models import Blog, LevelAccess, PaidFollow
from blogs.forms import BlogForm

from posts.models import Post
from posts.utils import get_views_and_comments_to_posts

from surveys.models import Survey
from surveys.utils import get_views_and_comments_to_surveys

from itertools import chain


@login_required(login_url="/registration/login")
def create(request):
    return render(
        request,
        "blogs/create.html",
        {"recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY},
    )


def show(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    posts = get_views_and_comments_to_posts(Post.objects.filter(blog=blog))
    surveys = get_views_and_comments_to_surveys(Survey.objects.filter(blog=blog))
    blog_list = list(chain(posts, surveys))

    paid_follow = PaidFollow.objects.filter(follower=request.user.id, blog=blog)
    if paid_follow:
        paid_follow = paid_follow[0]

    for e in blog_list:
        e.is_private = False
        if int(e.level_access) > 1:
            level_access = get_object_or_404(
                LevelAccess, blog=blog, level=e.level_access
            )
            e.scores_to_follow = level_access.scores
            e.is_private = True

        e.is_followed = False
        if paid_follow and paid_follow.blog_access_level.level >= e.level_access:
            e.is_followed = True

    paginator = Paginator(blog_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    data = {
        "blog": blog,
        "page_obj": page_obj,
        "paid_follow": paid_follow,
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }

    return render(request, "blogs/show.html", data)


def edit(request, slug):
    instance = get_object_or_404(Blog, user=request.user.id, slug=slug)

    form = BlogForm(instance=instance)

    data = {
        "form": form,
        "blog_id": instance.id,
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }

    return render(request, "blogs/edit.html", data)
