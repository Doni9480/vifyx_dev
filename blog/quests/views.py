from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from comments.models import Comment, Answer
from .models import Quest, QuestionQuest, QuestionQuestAnswer
from django.core.paginator import Paginator
from django.conf import settings
from .forms import QuestForm, QuestionForm, QuestionAnswerForm

# def create_quest(requests, **kwargs):


def list_quests(request):
    obj_set = Quest.objects.filter(language=request.user.language).order_by("scores")
    paginator = Paginator(obj_set, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    for quest_obj in page_obj.object_list:
        count_comments = Comment.objects.filter(quest=quest_obj).count()
        count_answers = Answer.objects.filter(quest=quest_obj).count()
        count_comments = count_comments + count_answers
        quest_obj.count_comments = count_comments
    return render(
        request, "quests/quests_list.html", {"tests": obj_set, "page_obj": page_obj}
    )


def detail_quest(request, slug):
    quest_obj = get_object_or_404(Quest, language=request.user.language, slug=slug)

    comment = Comment.objects.filter(quest=quest_obj)
    comment_answers = Answer.objects.filter(quest=quest_obj)
    count_comments = comment.count() + comment_answers.count()

    data = {
        "quest": quest_obj,
        # 'tags': tags,
        "comments": comment,
        "answers": comment_answers,
        "count_comments": count_comments,
        # 'count_views': count_views,
        # 'options': options,
        # 'vote': vote,
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }

    return render(request, "quests/quest_detail.html", data)


@login_required(login_url="/registration/login")
def quest_create(request):
    if request.method == "GET":
        form = QuestForm()
        return render(
            request,
            "quests/quest_create.html",
            {"form": form, "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY},
        )


def quest_edit(request, slug):
    instance = get_object_or_404(Quest, slug=slug)
    if instance.user != request.user:
        raise Http404
    if request.method == "GET":
        form = QuestForm(instance=instance)
        return render(
            request,
            "quests/quest_edit.html",
            {
                "form": form,
                "quest_id": instance.id,
                "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
            },
        )
        

@login_required(login_url="/registration/login")
def quest_question_cerate(request, slug):
    if request.method == "GET":
        quest_obj = get_object_or_404(Quest, slug=slug)
        form = QuestionForm()
        form_answer = QuestionAnswerForm()
        return render(
            request,
            "quests/question_cerate.html",
            {
                "form": form,
                "form_answer": form_answer,
                "quest_obj": quest_obj,
                "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
            },
        )


@login_required(login_url="/registration/login")
def quest_question_edit(request, slug, question_id):
    if request.method == "GET":
        quest_obj = get_object_or_404(Quest, slug=slug)
        question_obj = get_object_or_404(QuestionQuest, pk=question_id)
        q_answer_list = QuestionQuestAnswer.objects.filter(question=question_obj)
        return render(
            request,
            "quests/question_edit.html",
            {
                "question": question_obj,
                "question_answer": q_answer_list,
                "quest_obj": quest_obj,
                "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
            },
        )

