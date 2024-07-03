from django.contrib import admin

from posts.models import Post, PostTag, PostView


admin.site.register(Post)
admin.site.register(PostTag)
admin.site.register(PostView)