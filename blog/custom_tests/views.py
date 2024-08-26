from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from comments.models import Comment, Answer
from .models import Test, Question, QuestionAnswer, TestView, Category, Subcategory, TestLike
from custom_tests.utils import get_more_to_tests
from django.core.paginator import Paginator
from django.conf import settings
from posts.models import Post
from .forms import TestForm, QuestionForm, QuestionAnswerForm
from blogs.models import LevelAccess, Blog, BlogFollow
from users.utils import opening_access
from blogs.utils import get_obj_set, get_filter_kwargs, get_category

from operator import attrgetter


@login_required(login_url="/registration/login")
def test_create(request, slug):
    blog = get_object_or_404(Blog, slug=slug, user=request.user.id)
    level_follows = LevelAccess.objects.filter(blog=blog)
    categories = Category.objects.all()
    if request.method == "GET":
        form = TestForm()
        return render(
            request,
            "custom_test/test_create.html",
            {
                "form": form, 
                "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
                "blog": blog,
                "categories": categories,
                "level_follows": level_follows,
            },
        )


def test_edit(request, slug):
    instance = get_object_or_404(Test, slug=slug)
    blog = get_object_or_404(Blog, id=instance.blog.pk, user=request.user.id)
    level_follows = LevelAccess.objects.filter(blog=blog)
    categories = Category.objects.all()
    subcategories = Subcategory.objects.filter(category=instance.category)
    if instance.user != request.user:
        raise Http404()
    if request.method == "GET":
        form = TestForm(instance=instance)
        return render(
            request,
            "custom_test/test_edit.html",
            {
                "form": form,
                "test_id": instance.id,
                "categories": categories,
                "subcategories": subcategories,
                "level_follows": level_follows,
                "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
            },
        )


def list_tests(request):
    filter_kwargs, subcategories, select_subcategories = get_category(get_filter_kwargs(request), request, 'tests')
    if filter_kwargs.get('category'):
        select_category = True
    else:
        select_category = False
    
    obj_set = get_obj_set(Test.level_access_objects.filter(**filter_kwargs).order_by("scores"), request.user)
    obj_set = sorted(obj_set, key=attrgetter('date'), reverse=True)
    
    paginator = Paginator(obj_set, 5)
    page_number = request.GET.get("page")
    page_obj = get_more_to_tests(paginator.get_page(page_number))
        
    categories = Category.objects.all()
        
    return render(
        request, "custom_test/test_list.html", {
            "tests": obj_set, 
            "page_obj": page_obj,
            "categories": categories,
            "subcategories": subcategories,
            "select_subcategories": select_subcategories,
            "more_sub": len(list(select_subcategories)) == len(list(subcategories)),
            "select_category": select_category,
            "category_namespace": "tests",
            "there_category": request.user.tests_category if not request.user.is_anonymous else None,
        }
    )


def detail_test(request, slug):
    test_obj = get_object_or_404(Test.objects_show, slug=slug)
    opening_access(test_obj, request.user, is_show=True)

    comment_for_test = Comment.objects.filter(test=test_obj)
    comment_for_test_answers = Answer.objects.filter(test=test_obj)
    count_comments = comment_for_test.count() + comment_for_test_answers.count()
    count_views = TestView.objects.filter(test=test_obj).count()
    count_likes = TestLike.objects.filter(test=test_obj).count()

    data = {
        "test": test_obj,
        'follow_exists': bool(request.user != test_obj.user),
        'follow': bool(not BlogFollow.objects.filter(follower=request.user.id, blog=test_obj.blog)),
        # 'tags': tags,
        "comments": comment_for_test,
        "answers": comment_for_test_answers,
        "count_comments": count_comments,
        'count_views': count_views,
        # 'options': options,
        # 'vote': vote,
        'count_likes': count_likes,
        'is_like': bool(TestLike.objects.filter(test=test_obj, user=request.user.id)),
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }

    return render(request, "custom_test/test_detail.html", data)


@login_required(login_url="/registration/login")
def test_question_create(request, slug):
    if request.method == "GET":
        test_obj = get_object_or_404(Test, slug=slug)
        post = Post.objects.filter(test=test_obj.pk).first()
        form = QuestionForm()
        form_answer = QuestionAnswerForm()
        return render(
            request,
            "custom_test/question_create.html",
            {
                "form": form,
                "form_answer": form_answer,
                "test_obj": test_obj,
                "post": post,
                "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
            },
        )


@login_required(login_url="/registration/login")
def test_question_edit(request, slug, question_id):
    if request.method == "GET":
        test_obj = get_object_or_404(Test, slug=slug)
        post = Post.objects.filter(test=test_obj.pk).first()
        post_slug = None
        if post: post_slug = post.slug
        question_obj = get_object_or_404(Question, pk=question_id)
        q_answer_list = QuestionAnswer.objects.filter(question=question_obj)
        return render(
            request,
            "custom_test/question_edit.html",
            {
                "question": question_obj,
                "question_answer": q_answer_list,
                "test_obj": test_obj,
                "post_slug": post_slug,
                "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
            },
        )


def test_run(request, slug):
    test_obj = get_object_or_404(Test, slug=slug)
    opening_access(test_obj, request.user)
    # questions = Question.objects.filter(test=test_obj).order_by("id")
    # number = request
    return render(
        request,
        "custom_test/test_run.html",
        {
            "test": test_obj,
            # "questions": questions,
            "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        },
    )
