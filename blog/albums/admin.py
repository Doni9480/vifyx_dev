from django.contrib import admin
from unfold.admin import ModelAdmin
from albums.models import Album, AlbumView, Category, Subcategory

# admin.site.register(Album)
# admin.site.register(AlbumView)
# admin.site.register(Category)
# admin.site.register(Subcategory)



@admin.register(Album)
class AlbumAdmin(ModelAdmin):
    pass

@admin.register(Category)
class AlbumAdmin(ModelAdmin):
    pass

@admin.register(Subcategory)
class AlbumAdmin(ModelAdmin):
    pass

@admin.register(AlbumView)
class AlbumAdmin(ModelAdmin):
    pass