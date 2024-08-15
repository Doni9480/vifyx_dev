from django.contrib import admin
from unfold.admin import ModelAdmin
from posts.models import Post, PostTag, PostView, Category, Subcategory, Banner


@admin.register(Post)
class PostAdmin(ModelAdmin):
    pass


@admin.register(PostTag)
class PostTagAdmin(ModelAdmin):
    pass


@admin.register(PostView)
class PostViewAdmin(ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass


@admin.register(Subcategory)
class SubcategoryAdmin(ModelAdmin):
    pass

@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    pass
