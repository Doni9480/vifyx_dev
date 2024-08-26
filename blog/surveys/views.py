from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.http import Http404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from surveys.models import Survey, SurveyTag, SurveyRadio, SurveyView, SurveyVote, DraftSurvey, DraftSurveyTag, DraftSurveyRadio, Category, Subcategory, SurveyLike
from surveys.forms import SurveyForm, DraftSurveyForm
from surveys.utils import get_more_to_surveys
from comments.models import Comment, Answer

from blogs.models import LevelAccess, Blog, BlogFollow
from users.utils import opening_access
from blogs.utils import get_obj_set, get_filter_kwargs, get_category

from operator import attrgetter


def index(request):
    filter_kwargs, subcategories, select_subcategories = get_category(get_filter_kwargs(request), request, 'surveys')
    if filter_kwargs.get('category'):
        select_category = True
    else:
        select_category = False

    obj_set = get_obj_set(Survey.level_access_objects.filter(**filter_kwargs), request.user)
    obj_set = sorted(obj_set, key=attrgetter('date'), reverse=True)       

    paginator = Paginator(obj_set, 5)
    page_number = request.GET.get("page")
    page_obj = get_more_to_surveys(paginator.get_page(page_number))
    
    categories = Category.objects.all()

    return render(request, 'surveys/index.html', {
        "page_obj": page_obj, 
        "categories": categories,
        "subcategories": subcategories,
        "select_subcategories": select_subcategories,
        "more_sub": len(list(select_subcategories)) == len(list(subcategories)),
        "select_category": select_category,
        "category_namespace": "surveys",
        "there_category": request.user.surveys_category if not request.user.is_anonymous else None,
    })

@login_required(login_url='/registration/login')
def create(request, slug):
    blog = get_object_or_404(Blog, slug=slug, user=request.user.id)
    
    if DraftSurvey.objects.filter(user=request.user.id, blog=blog):
        return redirect('surveys:draft_survey_create', blog.slug)
    
    form = SurveyForm()
    
    level_follows = LevelAccess.objects.filter(blog=blog)
    categories = Category.objects.all()
    
    data = {
        'form': form, 
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        'blog': blog,
        "categories": categories,
        'level_follows': level_follows,
    }

    return render(request, 'surveys/create.html', data)

def edit(request, slug):
    instance = get_object_or_404(Survey.objects, slug=slug, user=request.user.id)
    blog = get_object_or_404(Blog, id=instance.blog.pk, user=request.user.id)
    
    tags = SurveyTag.objects.filter(survey=instance)
    for tag in tags:
        tag.replaced = tag.title.replace(' ', '_')
        
    answers = SurveyRadio.objects.filter(survey=instance)
    form = SurveyForm(instance=instance)
    level_follows = LevelAccess.objects.filter(blog=blog)
    categories = Category.objects.all()
    subcategories = Subcategory.objects.filter(category=instance.category)
    
    data = {
        'level_follows': level_follows,
        'answers': answers,
        'form': form,
        'tags': tags,
        'survey_id': instance.id,
        "categories": categories,
        "subcategories": subcategories,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY
    }
    
    return render(request, 'surveys/edit.html', data)

def show(request, slug):
    survey = get_object_or_404(Survey.objects, slug=slug)        
    opening_access(survey, request.user, is_show=True)
    comments = Comment.objects.filter(survey=survey) 
    answers = Answer.objects.filter(survey=survey)
    count_comments = comments.count() + answers.count()
    options = SurveyRadio.objects.filter(survey=survey)

    tags = SurveyTag.objects.filter(survey=survey)
    
    count_views = SurveyView.objects.filter(survey=survey).count()
    
    count_likes = SurveyLike.objects.filter(survey=survey).count()

    vote = False
    votes_user = SurveyVote.objects.filter(user=request.user.id, survey=survey)

    total_scores = sum(option.scores for option in options)
    for option in options:
        try:
            option.percent = round(option.scores / total_scores * 100)
        except ZeroDivisionError:
            option.percent = 0

    for option in options:
        total_scores += option.scores

        vote_model = votes_user.filter(option=option)
        if vote_model:
            vote = vote_model[0]
            break
    
    data = {
        'survey': survey,
        'follow_exists': bool(request.user != survey.user),
        'follow': bool(not BlogFollow.objects.filter(follower=request.user.id, blog=survey.blog)),
        'tags': tags,
        'comments': comments,
        'answers': answers,
        'count_comments': count_comments,
        'count_views': count_views,
        'options': options,
        'vote': vote,
        'count_likes': count_likes,
        'is_like': bool(SurveyLike.objects.filter(survey=survey, user=request.user.id)),
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY
    }
    
    return render(request, 'surveys/show.html', data)

# draft
@login_required(login_url='/registration/login')
def draft_survey_create(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    draft_survey = get_object_or_404(DraftSurvey, user=request.user.id, blog=blog)
    
    categories = Category.objects.all()
    subcategories = Subcategory.objects.filter(category=draft_survey.category)
    form = DraftSurveyForm(instance=draft_survey)
    tags = DraftSurveyTag.objects.filter(draft_survey=draft_survey)
    for tag in tags:
        tag.replaced = tag.title.replace(' ', '_')
        
    answers = DraftSurveyRadio.objects.filter(draft_survey=draft_survey)
    
    level_follows = LevelAccess.objects.filter(blog=blog)
    
    data = {
        'form': form,
        'draft_survey': draft_survey,
        'tags': tags,
        'answers': answers,
        'blog': blog,
        'categories': categories,
        'subcategories': subcategories,
        'level_follows': level_follows,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }
    
    return render(request, 'drafts_survey/create.html', data)