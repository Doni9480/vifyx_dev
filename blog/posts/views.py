from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator

from posts.forms import PostForm, DraftForm
from posts.models import PostTag, Post, PostView, DraftPost
from posts.utils import opening_access

from users.models import Follow

from comments.models import Comment, Answer

from blogs.models import Blog, LevelAccess


# def index(request):        
#     posts_list = Post.level_access_objects.all().order_by('-date')
#     paginator = Paginator(posts_list, 5)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)
#     for post in page_obj:
#         count_comments = Comment.objects.filter(post=post).count()
#         count_answers = Answer.objects.filter(post=post).count()
#         count_comments = count_comments + count_answers
#         post.count_comments = count_comments
        
#         count_views = View.objects.filter(post=post).count()
#         post.count_views = count_views
     
#     return render(request, 'posts/index.html', {'page_obj': page_obj, 'range': range(1, page_obj.paginator.num_pages)})

@login_required(login_url='/registration/login')
def create(request, slug):
    blog = get_object_or_404(Blog, slug=slug, user=request.user.id)
    
    if DraftPost.objects.filter(user=request.user.id, blog=blog):
        return redirect('drafts:create', blog.slug)
    
    blog_levels = LevelAccess.objects.filter(blog=blog)
    
    form = PostForm()
    
    data = {
        'form': form, 
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        'blog': blog,
        'blog_levels': blog_levels,
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
    
    count_views = PostView.objects.filter(post=post).count()
    
    data = {
        'post': post,
        'follow_exists': bool(request.user != post.user),
        'follow': bool(not Follow.objects.filter(follower=request.user.id, user=post.user)),
        'tags': tags,
        'comments': comments,
        'answers': answers,
        'count_comments': count_comments,
        'count_views': count_views,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY
    }
    
    return render(request, 'posts/show.html', data)

def edit(request, slug):
    instance = get_object_or_404(Post.objects, slug=slug, user=request.user.id)
    blog = get_object_or_404(Blog, id=instance.blog.pk, user=request.user.id)
    
    tags = PostTag.objects.filter(post=instance)
    for tag in tags:
        tag.replaced = tag.title.replace(' ', '_')
        
    form = PostForm(instance=instance)
    
    blog_levels = LevelAccess.objects.filter(blog=blog)
    
    data = {
        'blog_levels': blog_levels,
        'form': form,
        'tags': tags,
        'post_id': instance.id,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY
    }
    
    return render(request, 'posts/edit.html', data)

def best_posts_mouth(request):
    posts = Post.level_access_objects.filter(language=request.user.language).order_by('mouth_scores')[:5]
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
        draft = get_object_or_404(DraftPost, user=request.user.id, blog=blog)
    except Exception:
        raise Http404()
    
    form = DraftForm(instance=draft)
    tags = PostTag.objects.filter(draft=draft)
    for tag in tags:
        tag.replaced = tag.title.replace(' ', '_')
        
    blog_levels = LevelAccess.objects.filter(blog=blog)
    
    data = {
        'form': form,
        'draft': draft,
        'tags': tags,
        'blog': blog,
        'blog_levels': blog_levels,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }
    
    return render(request, 'drafts/create.html', data)