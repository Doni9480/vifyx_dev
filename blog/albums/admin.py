from django.contrib import admin
from albums.models import Album, AlbumView, Category, Subcategory


admin.site.register(Album)
admin.site.register(AlbumView)
admin.site.register(Category)
admin.site.register(Subcategory)