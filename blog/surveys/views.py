from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.http import Http404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from surveys.models import Survey, SurveyTag, SurveyRadio, SurveyView, SurveyVote, DraftSurvey
from surveys.forms import SurveyForm, DraftSurveyForm
from surveys.utils import get_views_and_comments_to_surveys, opening_access
from comments.models import Comment, Answer

from blogs.models import LevelAccess, Blog
from users.models import Follow

def index(request):
    if not request.user.is_staff:
        surveys_list = Survey.level_access_objects.filter(hide_to_user=False, hide_to_moderator=False, language=request.user.language).order_by('-date')
    else:
        surveys_list = Survey.level_access_objects.filter(language=request.user.language).order_by('-date')
        
    paginator = Paginator(surveys_list, 5)
    page_number = request.GET.get("page")
    page_obj = get_views_and_comments_to_surveys(paginator.get_page(page_number))

    return render(request, 'surveys/index.html', {'page_obj': page_obj})

@login_required(login_url='/registration/login')
def create(request, slug):
    blog = get_object_or_404(Blog, slug=slug, user=request.user.id)
    
    if DraftSurvey.objects.filter(user=request.user.id, blog=blog):
        return redirect('drafts_survey:create', blog.slug)
    
    form = SurveyForm()
    
    blog_levels = LevelAccess.objects.filter(blog=blog)
    
    data = {
        'form': form, 
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        'blog': blog,
        'blog_levels': blog_levels,
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
    
    blog_levels = LevelAccess.objects.filter(blog=blog)
    
    data = {
        'blog_levels': blog_levels,
        'answers': answers,
        'form': form,
        'tags': tags,
        'survey_id': instance.id,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY
    }
    
    return render(request, 'surveys/edit.html', data)

def show(request, slug):
    survey = get_object_or_404(Survey.objects, slug=slug)        
    if opening_access(survey, request.user):
        raise Http404()

    comments = Comment.objects.filter(survey=survey) 
    answers = Answer.objects.filter(survey=survey)
    count_comments = comments.count() + answers.count()
    
    options = SurveyRadio.objects.filter(survey=survey)

    tags = SurveyTag.objects.filter(survey=survey)
    
    count_views = SurveyView.objects.filter(survey=survey).count()

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
        'follow': bool(not Follow.objects.filter(follower=request.user.id, user=survey.user)),
        'tags': tags,
        'comments': comments,
        'answers': answers,
        'count_comments': count_comments,
        'count_views': count_views,
        'options': options,
        'vote': vote,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY
    }
    
    return render(request, 'surveys/show.html', data)

# draft
@login_required(login_url='/registration/login')
def draft_survey_create(request, slug):
    try:
        blog = get_object_or_404(Blog, slug=slug)
        draft_survey = get_object_or_404(DraftSurvey, user=request.user.id, blog=blog)
    except Exception:
        raise Http404()
    
    form = DraftSurveyForm(instance=draft_survey)
    tags = SurveyTag.objects.filter(draft_survey=draft_survey)
    for tag in tags:
        tag.replaced = tag.title.replace(' ', '_')
        
    answers = SurveyRadio.objects.filter(draft_survey=draft_survey)
    
    blog_levels = LevelAccess.objects.filter(blog=blog)
    
    data = {
        'form': form,
        'draft_survey': draft_survey,
        'tags': tags,
        'answers': answers,
        'blog': blog,
        'blog_levels': blog_levels,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }
    
    return render(request, 'drafts_survey/create.html', data)