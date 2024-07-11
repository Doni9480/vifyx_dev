from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from comments.models import Comment, Answer
from .models import Test, Question, QuestionAnswer
from django.core.paginator import Paginator
from django.conf import settings
from .forms import TestForm, QuestionForm, QuestionAnswerForm


@login_required(login_url="/registration/login")
def test_create(request):
    if request.method == "GET":
        form = TestForm()
        return render(
            request,
            "custom_test/test_create.html",
            {"form": form, "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY},
        )
    if request.method == "POST":
        form = TestForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.language = request.user.language
            form.save()
            return redirect("custom_test:list_tests")
        return render(
            request,
            "custom_test/test_create.html",
            {"form": form, "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY},
        )


def test_edit(request, slug):
    instance = get_object_or_404(Test, slug=slug)
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
                "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
            },
        )
    if request.method == "POST":
        form = TestForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.language = request.user.language
            form.save()
            return redirect("custom_test:list_tests")
        return render(request, "custom_test/test_edit.html", {"form": form})


def list_tests(request):
    filter_kwargs = {}
    if request.user.language != 'any':
        filter_kwargs['language'] = request.user.language
    obj_set = Test.objects.filter(**filter_kwargs).order_by("scores")
    paginator = Paginator(obj_set, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    for test_obj in page_obj.object_list:
        count_comments = Comment.objects.filter(test=test_obj).count()
        count_answers = Answer.objects.filter(test=test_obj).count()
        count_comments = count_comments + count_answers
        test_obj.count_comments = count_comments
    return render(
        request, "custom_test/test_list.html", {"tests": obj_set, "page_obj": page_obj}
    )


def detail_test(request, slug):
    filter_kwargs = {'slug': slug}
    if request.user.language != 'any':
        filter_kwargs['language'] = request.user.language
    test_obj = get_object_or_404(Test, **filter_kwargs)

    comment_for_test = Comment.objects.filter(test=test_obj)
    comment_for_test_answers = Answer.objects.filter(test=test_obj)
    count_comments = comment_for_test.count() + comment_for_test_answers.count()

    data = {
        "test": test_obj,
        # 'tags': tags,
        "comments": comment_for_test,
        "answers": comment_for_test_answers,
        "count_comments": count_comments,
        # 'count_views': count_views,
        # 'options': options,
        # 'vote': vote,
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }

    return render(request, "custom_test/test_detail.html", data)


@login_required(login_url="/registration/login")
def test_question_create(request, slug):
    if request.method == "GET":
        test_obj = get_object_or_404(Test, slug=slug)
        form = QuestionForm()
        form_answer = QuestionAnswerForm()
        return render(
            request,
            "custom_test/question_create.html",
            {
                "form": form,
                "form_answer": form_answer,
                "test_obj": test_obj,
                "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
            },
        )


@login_required(login_url="/registration/login")
def test_question_edit(request, slug, question_id):
    if request.method == "GET":
        test_obj = get_object_or_404(Test, slug=slug)
        question_obj = get_object_or_404(Question, pk=question_id)
        q_answer_list = QuestionAnswer.objects.filter(question=question_obj)
        return render(
            request,
            "custom_test/question_edit.html",
            {
                "question": question_obj,
                "question_answer": q_answer_list,
                "test_obj": test_obj,
                "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
            },
        )


def test_run(request, slug):
    filter_kwargs = {'slug': slug}
    if request.user.language != 'any':
        filter_kwargs['language'] = request.user.language
    test_obj = get_object_or_404(Test, **filter_kwargs)
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
