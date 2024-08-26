from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator

from posts.forms import PostForm, DraftForm
from posts.models import (
    PostTag, 
    Post, 
    PostView, 
    DraftPost, 
    DraftPostTag, 
    BuyPost, 
    PostRadio, 
    DraftPostRadio,
    PostVote,
    Category,
    Subcategory,
    PostLike,
)
from users.utils import opening_access
from posts.utils import get_more_to_posts
from blogs.utils import get_filter_kwargs, get_obj_set, get_category, slice_content
from comments.models import Comment, Answer
from blogs.models import Blog, LevelAccess, BlogFollow
from contests.models import PostElement

from operator import attrgetter


def index(request):
    filter_kwargs, subcategories, select_subcategories = get_category(get_filter_kwargs(request), request, 'posts')
    if filter_kwargs.get('category'):
        select_category = True
    else:
        select_category = False

    obj_set = get_obj_set(Post.level_access_objects.filter(**filter_kwargs).order_by('-date'), request.user)
    obj_set = sorted(obj_set, key=attrgetter('date'), reverse=True)
    
    categories = Category.objects.all()

    paginator = Paginator(obj_set, 5)
    page_number = request.GET.get("page")
    page_obj = get_more_to_posts(paginator.get_page(page_number))
    return render(request, 'posts/index.html', {
        'page_obj': page_obj, 
        'categories': categories,
        "subcategories": subcategories,
        "select_subcategories": select_subcategories,
        "more_sub": len(list(select_subcategories)) == len(list(subcategories)),
        "select_category": select_category,
        "category_namespace": "posts",
        "there_category": request.user.posts_category if not request.user.is_anonymous else None,
    })

@login_required(login_url='/registration/login')
def create(request, slug):
    blog = get_object_or_404(Blog, slug=slug, user=request.user.id)
    
    if DraftPost.objects.filter(user=request.user.id, blog=blog):
        return redirect('posts:draft_post_create', blog.slug)
    
    level_follows = LevelAccess.objects.filter(blog=blog)
    categories = Category.objects.all()
    
    form = PostForm()
    
    data = {
        'form': form, 
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        'blog': blog,
        'categories': categories,
        'level_follows': level_follows,
    }
    return render(request, 'posts/create.html', data)
    
def show(request, slug):
    post = get_object_or_404(Post.objects, slug=slug)
    opening_access(post, request.user, is_show=True)
    
    buy_post = BuyPost.objects.filter(user=request.user.id, post=post)
    if post.is_paid and not buy_post and request.user != post.user:
        post.content = slice_content(post.content)
    
    comments = Comment.objects.filter(post=post)
        
    answers = Answer.objects.filter(post=post)
    count_comments = comments.count() + answers.count()
    
    count_likes = PostLike.objects.filter(post=post).count()

    tags = PostTag.objects.filter(post=post)
    
    
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
    
    questions = []
    if post.test:
        questions = post.test.questions.all()
        
    post_element = PostElement.objects.filter(post=post).first()
    contest = post_element.contest if post_element else None
    
    data = {
        'post': post,
        'follow_exists': bool(request.user != post.user),
        'follow': bool(not BlogFollow.objects.filter(follower=request.user.id, blog=post.blog)),
        'no_buy_post': bool(post.is_paid and not buy_post),
        'tags': tags,
        'comments': comments,
        'answers': answers,
        'count_comments': count_comments,
        'count_views': count_views,
        'options': options,
        'vote': vote,
        'questions': questions,
        'count_likes': count_likes,
        'is_like': bool(PostLike.objects.filter(post=post, user=request.user.id)),
        'contest': contest,
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
    level_follows = LevelAccess.objects.filter(blog=blog)
    categories = Category.objects.all()
    subcategories = Subcategory.objects.filter(category=instance.category)
    
    data = {
        'level_follows': level_follows,
        'form': form,
        'answers': answers,
        'tags': tags,
        'post_id': instance.id,
        "categories": categories,
        "subcategories": subcategories,
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
    blog = get_object_or_404(Blog, slug=slug)
    draft = get_object_or_404(DraftPost, user=request.user, blog=blog)
    
    form = DraftForm(instance=draft)
    tags = DraftPostTag.objects.filter(draft=draft)
    for tag in tags:
        tag.replaced = tag.title.replace(' ', '_')
        
    level_follows = LevelAccess.objects.filter(blog=blog)
    categories = Category.objects.all()
    subcategories = Subcategory.objects.filter(category=draft.category)
    answers = DraftPostRadio.objects.filter(draft_post=draft)
        
    data = {
        'form': form,
        'draft': draft,
        'tags': tags,
        'blog': blog,
        'answers': answers,
        'categories': categories,
        'subcategories': subcategories,
        'level_follows': level_follows,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }
    
    return render(request, 'drafts/create.html', data)