from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator

from posts.forms import PostForm, DraftForm, QuestionForm, QuestionAnswerForm
from posts.models import (
    PostTag, 
    Post, 
    PostView, 
    DraftPost, 
    DraftPostTag, 
    BuyPost, 
    PostRadio, 
    DraftPostRadio,
    Question,
    QuestionAnswer,
    PostVote
)
from posts.utils import opening_access, get_views_and_comments_to_posts

from blog.translations import main_dict

from comments.models import Comment, Answer

from blogs.models import Blog, LevelAccess, BlogFollow


def main(request):
    filter_kwargs = {'hide_to_user': False, 'hide_to_moderator': False, 'language': request.user.language}
    if request.user.language == 'any':
        del filter_kwargs['language']
    if request.user.is_staff:
        del filter_kwargs['hide_to_moderator']
        del filter_kwargs['hide_to_user']
        
    posts = Post.level_access_objects.filter(**filter_kwargs).order_by('-date')[:20]

    paginator = Paginator(get_views_and_comments_to_posts(posts), 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    data = dict(
        list({"page_obj": page_obj}.items())
        + list(main_dict[request.user.language].items())
    )

    return render(request, "main.html", data)

@login_required(login_url='/registration/login')
def create(request, slug):
    blog = get_object_or_404(Blog, slug=slug, user=request.user.id)
    
    if DraftPost.objects.filter(user=request.user.id, blog=blog):
        return redirect('posts:draft_post_create', blog.slug)
    
    level_follows = LevelAccess.objects.filter(blog=blog)
    
    form = PostForm()
    
    data = {
        'form': form, 
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        'blog': blog,
        'level_follows': level_follows,
    }
    return render(request, 'posts/create.html', data)
    
def show(request, slug):
    post = get_object_or_404(Post.objects, slug=slug)
    if opening_access(post, request.user):
        raise Http404()
    
    comments = Comment.objects.filter(post=post)
        
    answers = Answer.objects.filter(post=post)
    count_comments = comments.count() + answers.count()    

    tags = PostTag.objects.filter(post=post)
    
    questions = post.questions.all()
    
    count_views = PostView.objects.filter(post=post).count()
    
    options = PostRadio.objects.filter(post=post)
    vote = False
    votes_user = PostVote.objects.filter(user=request.user.id, post=post)

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
        'post': post,
        'follow_exists': bool(request.user != post.user),
        'follow': bool(not BlogFollow.objects.filter(follower=request.user.id, blog=post.blog)),
        'no_buy_post': bool(post.is_paid and not BuyPost.objects.filter(user=request.user.id, post=post)),
        'tags': tags,
        'comments': comments,
        'answers': answers,
        'count_comments': count_comments,
        'questions': questions,
        'count_views': count_views,
        'options': options,
        'vote': vote,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY
    }
    
    return render(request, 'posts/show.html', data)

def edit(request, slug):
    instance = get_object_or_404(Post.objects, slug=slug, user=request.user.id)
    blog = get_object_or_404(Blog, id=instance.blog.pk, user=request.user.id)
    
    tags = PostTag.objects.filter(post=instance)
    for tag in tags:
        tag.replaced = tag.title.replace(' ', '_')
        
    answers = PostRadio.objects.filter(post=instance)
    form = PostForm(instance=instance)
    
    blog_levels = LevelAccess.objects.filter(blog=blog)
    
    data = {
        'blog_levels': blog_levels,
        'form': form,
        'answers': answers,
        'tags': tags,
        'post_id': instance.id,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY
    }
    
    return render(request, 'posts/edit.html', data)

def best_posts_mouth(request):
    filter_kwargs = {'hide_to_user': False, 'hide_to_moderator': False}
    if request.user.language != 'any':
        filter_kwargs['language'] = request.user.language
    posts = Post.level_access_objects.filter(**filter_kwargs).order_by('mouth_scores')[:5]
    for post in posts:
        count_comments = Comment.objects.filter(post=post).count()
        count_answers = Answer.objects.filter(post=post).count()
        count_comments = count_comments + count_answers
        post.count_comments = count_comments
        
        count_views = PostView.objects.filter(post=post).count()
        post.count_views = count_views
        
    return render(request, 'posts/best_posts_mouth.html', {'posts': posts})

#  draft
@login_required(login_url='/registration/login')
def draft_post_create(request, slug):
    try:

        blog = get_object_or_404(Blog, slug=slug)

        draft = get_object_or_404(DraftPost, user=request.user, blog=blog)
    except Exception:
        raise Http404()
    
    form = DraftForm(instance=draft)
    tags = DraftPostTag.objects.filter(draft=draft)
    for tag in tags:
        tag.replaced = tag.title.replace(' ', '_')
        
    level_follows = LevelAccess.objects.filter(blog=blog)
    
    answers = DraftPostRadio.objects.filter(draft_post=draft)
        
    data = {
        'form': form,
        'draft': draft,
        'tags': tags,
        'blog': blog,
        'answers': answers,
        'level_follows': level_follows,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }
    
    return render(request, 'drafts/create.html', data)

@login_required(login_url="/registration/login")
def post_question_create(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    form = QuestionForm()
    form_answer = QuestionAnswerForm()
    
    return render(
        request,
        "posts/question_create.html",
        {
            "form": form,
            "form_answer": form_answer,
            "post": post,
            "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        },
    )
    
@login_required(login_url="/registration/login")
def post_question_edit(request, slug, question_id):
    post = get_object_or_404(Post, slug=slug)
    question_obj = get_object_or_404(Question, pk=question_id)
    q_answer_list = QuestionAnswer.objects.filter(question=question_obj)
    return render(
        request,
        "posts/question_edit.html",
        {
            "question": question_obj,
            "question_answer": q_answer_list,
            "post": post,
            "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        },
    )

def test_run(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if opening_access(post, request.user):
        raise Http404()
    
    return render(
        request,
        "posts/test_run.html",
        {
            "post": post,
            'count_comments': Comment.objects.filter(post=post).count() + Answer.objects.filter(post=post).count(),
            'count_views': PostView.objects.filter(post=post).count(),
            "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        },
    )