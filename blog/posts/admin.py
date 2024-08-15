from django.contrib import admin

from posts.models import Post, PostTag, PostView, Category, Subcategory, Banner


admin.site.register(Post)
admin.site.register(PostTag)
admin.site.register(PostView)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Banner)