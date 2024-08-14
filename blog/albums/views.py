from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from blogs.utils import get_filter_kwargs, get_category, get_obj_set
from blogs.models import Blog, LevelAccess
from albums.utils import get_views_and_comments_to_albums
from albums.models import Album, Category, AlbumView, Subcategory, AlbumPhoto, DraftAlbum, DraftAlbumPhoto
from albums.forms import AlbumForm, DraftAlbumForm
from users.utils import opening_access
from blogs.models import BlogFollow
from comments.models import Answer, Comment
from operator import attrgetter


def index(request):
    filter_kwargs, subcategories, select_subcategories = get_category(get_filter_kwargs(request), request, 'albums')
    if filter_kwargs.get('category'):
        select_category = True
    else:
        select_category = False
        
    obj_set = get_obj_set(Album.level_access_objects.filter(**filter_kwargs).order_by('-date'), request.user)
    obj_set = sorted(obj_set, key=attrgetter('date'), reverse=True)
    
    categories = Category.objects.all()

    paginator = Paginator(obj_set, 5)
    page_number = request.GET.get("page")
    page_obj = get_views_and_comments_to_albums(paginator.get_page(page_number))
    return render(request, 'albums/index.html', {
        'page_obj': page_obj, 
        'categories': categories,
        "subcategories": subcategories,
        "select_category": select_category,
        "select_subcategories": select_subcategories,
        "more_sub": len(list(select_subcategories)) == len(list(subcategories)),
        "category_namespace": "albums",
        "there_category": request.user.albums_category if not request.user.is_anonymous else None,
    })
    
@login_required(login_url='/registration/login')
def create(request, slug):
    blog = get_object_or_404(Blog, slug=slug, user=request.user.id)
    
    if DraftAlbum.objects.filter(user=request.user.id, blog=blog):
        return redirect('albums:draft_album_create', blog.slug)
    
    level_follows = LevelAccess.objects.filter(blog=blog)
    categories = Category.objects.all()
    
    data = {
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        'blog': blog,
        'categories': categories,
        'level_follows': level_follows,
    }
    return render(request, 'albums/create.html', data)

def show(request, slug):
    album = get_object_or_404(Album.objects, slug=slug)
    opening_access(album, request.user, is_show=True)
    
    comments = Comment.objects.filter(album=album)
        
    answers = Answer.objects.filter(album=album)
    count_comments = comments.count() + answers.count()    
    
    count_views = AlbumView.objects.filter(album=album).count()
    
    photos = AlbumPhoto.objects.filter(album=album)
    
    data = {
        'album': album,
        'follow_exists': bool(request.user != album.user),
        'follow': bool(not BlogFollow.objects.filter(follower=request.user.id, blog=album.blog)),
        'comments': comments,
        'answers': answers,
        'photos': photos,
        'count_comments': count_comments,
        'count_views': count_views,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY
    }
    
    return render(request, 'albums/show.html', data)

def edit(request, slug):
    instance = get_object_or_404(Album.objects, slug=slug, user=request.user.id)
    blog = get_object_or_404(Blog, id=instance.blog.pk, user=request.user.id)
        
    form = AlbumForm(instance=instance)
    level_follows = LevelAccess.objects.filter(blog=blog)
    categories = Category.objects.all()
    subcategories = Subcategory.objects.filter(category=instance.category)
    photos = AlbumPhoto.objects.filter(album=instance)
    
    data = {
        "level_follows": level_follows,
        "form": form,
        "album_id": instance.id,
        "categories": categories,
        "subcategories": subcategories,
        "photos": photos,
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY
    }
    
    return render(request, 'albums/edit.html', data)

@login_required(login_url='/registration/login')
def draft_album_create(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    draft = get_object_or_404(DraftAlbum, user=request.user, blog=blog)
    
    form = DraftAlbumForm(instance=draft)
        
    level_follows = LevelAccess.objects.filter(blog=blog)
    categories = Category.objects.all()
    subcategories = Subcategory.objects.filter(category=draft.category)
    photos = DraftAlbumPhoto.objects.filter(draft_album=draft)
        
    data = {
        'form': form,
        'draft': draft,
        'blog': blog,
        'categories': categories,
        'subcategories': subcategories,
        'photos': photos,
        'level_follows': level_follows,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }
    
    return render(request, 'drafts_album/create.html', data)