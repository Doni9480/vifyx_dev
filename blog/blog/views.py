from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect

from posts.models import Post
from posts.utils import get_views_and_comments_to_posts

from surveys.models import Survey, SurveyRadio
from surveys.utils import get_views_and_comments_to_surveys

from blog.translations import main_dict

from itertools import chain

from operator import attrgetter


def redirect_main(request):
    return redirect("main")


def main(request):
    if not request.user.is_staff:
        posts = Post.level_access_objects.filter(
            hide_to_user=False, hide_to_moderator=False, language=request.user.language
        )
        surveys = Survey.level_access_objects.filter(
            hide_to_user=False, hide_to_moderator=False, language=request.user.language
        )
    else:
        posts = Post.level_access_objects.filter(language=request.user.language)
        surveys = Survey.level_access_objects.filter(language=request.user.language)

    posts = get_views_and_comments_to_posts(posts)
    surveys = get_views_and_comments_to_surveys(surveys)

    blogs_list = sorted(chain(posts, surveys), key=attrgetter("date"), reverse=True)[
        :20
    ]
    paginator = Paginator(blogs_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    data = dict(
        list({"page_obj": page_obj}.items())
        + list(main_dict[request.user.language - 1].items())
    )

    return render(request, "main.html", data)


def best_blogs(request):
    if not request.user.is_staff:
        posts = Post.level_access_objects.filter(
            hide_to_user=False, hide_to_moderator=False, language=request.user.language
        )
        surveys = Survey.level_access_objects.filter(
            hide_to_user=False, hide_to_moderator=False, language=request.user.language
        )
    else:
        posts = Post.level_access_objects.filter(language=request.user.language)
        surveys = Survey.level_access_objects.filter(language=request.user.language)

    posts = get_views_and_comments_to_posts(posts)
    surveys = get_views_and_comments_to_surveys(surveys)

    for survey in surveys:
        survey.scores = 0
        options = SurveyRadio.objects.filter(survey=survey)
        for option in options:
            survey.scores += option.scores

    blogs = sorted(chain(posts, surveys), key=attrgetter("scores"), reverse=True)[:5]

    return render(request, "popular.html", {"blogs": blogs})


def language(request, language):
    if language == "russian":
        cookie = "russian"
    else:
        cookie = "english"

    redirect = HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    redirect.set_cookie("language", cookie, max_age=31536000)
    return redirect
