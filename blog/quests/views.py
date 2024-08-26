from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from comments.models import Comment, Answer
from .models import (
    Quest, 
    QuestionQuest,
    QuestionQuestAnswer, 
    QuestView, 
    Category, 
    Subcategory, 
    QuestLike,
    QuestTag
)
from quests.utils import get_more_to_quests
from users.utils import opening_access
from django.core.paginator import Paginator
from django.conf import settings
from .forms import QuestForm, QuestionForm, QuestionAnswerForm
from blogs.models import Blog, LevelAccess, BlogFollow
from blogs.utils import get_obj_set, get_filter_kwargs, get_category
from contests.models import QuestElement

from operator import attrgetter


def list_quests(request):
    filter_kwargs, subcategories, select_subcategories = get_category(get_filter_kwargs(request), request, 'quests')
    if filter_kwargs.get('category'):
        select_category = True
    else:
        select_category = False
        
    obj_set = get_obj_set(Quest.level_access_objects.filter(**filter_kwargs), request.user)
    obj_set = sorted(obj_set, key=attrgetter('date'), reverse=True)
    
    paginator = Paginator(obj_set, 5)
    page_number = request.GET.get("page")
    page_obj = get_more_to_quests(paginator.get_page(page_number))
    
    categories = Category.objects.all()
        
    return render(
        request, "quests/quests_list.html", {
            "tests": obj_set, 
            "page_obj": page_obj,
            "categories": categories,
            "subcategories": subcategories,
            "select_subcategories": select_subcategories,
            "more_sub": len(list(select_subcategories)) == len(list(subcategories)),
            "select_category": select_category,
            "category_namespace": "quests",
            "there_category": request.user.quests_category if not request.user.is_anonymous else None,
        }
    )


def detail_quest(request, slug):
    filter_kwargs = {'slug': slug}
    if request.user.language != 'any':
        filter_kwargs['language'] = request.user.language
    quest_obj = get_object_or_404(Quest, **filter_kwargs)
    opening_access(quest_obj, request.user, is_show=True)

    comment = Comment.objects.filter(quest=quest_obj)
    comment_answers = Answer.objects.filter(quest=quest_obj)
    count_comments = comment.count() + comment_answers.count()
    
    count_views = QuestView.objects.filter(quest=quest_obj).count()
    
    count_likes = QuestLike.objects.filter(quest=quest_obj).count()
    
    tags = QuestTag.objects.filter(quest=quest_obj)
    
    quest_element = QuestElement.objects.filter(quest=quest_obj).first()
    contest = quest_element.contest if quest_element else None

    data = {
        "quest": quest_obj,
        'follow_exists': bool(request.user != quest_obj.user),
        'follow': bool(not BlogFollow.objects.filter(follower=request.user.id, blog=quest_obj.blog)),
        # 'tags': tags,
        "comments": comment,
        "answers": comment_answers,
        "count_comments": count_comments,
        "count_views": count_views,
        "count_likes": count_likes,
        "tags": tags,
        "is_like": bool(QuestLike.objects.filter(quest=quest_obj, user=request.user.id)),
        "contest": contest,
        # 'options': options,
        # 'vote': vote,
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }

    return render(request, "quests/quest_detail.html", data)


@login_required(login_url="/registration/login")
def quest_create(request, slug):
    blog = get_object_or_404(Blog, slug=slug, user=request.user.id)
    categories = Category.objects.all()
    level_follows = LevelAccess.objects.filter(blog=blog)
    if request.method == "GET":
        form = QuestForm()
        return render(
            request,
            "quests/quest_create.html",
            {
                "form": form, 
                "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY, 
                'level_follows': level_follows, 
                "categories": categories,
                'blog': blog
            },
        )


def quest_edit(request, slug):
    instance = get_object_or_404(Quest, slug=slug)
    blog = get_object_or_404(Blog, id=instance.blog.pk, user=request.user.id)
    level_follows = LevelAccess.objects.filter(blog=blog)
    categories = Category.objects.all()
    subcategories = Subcategory.objects.filter(category=instance.category)
    tags = QuestTag.objects.filter(quest=instance)
    for tag in tags:
        tag.replaced = tag.title.replace(' ', '_')
        
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
                "categories": categories,
                "subcategories": subcategories,
                "level_follows": level_follows,
                "tags": tags,
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

