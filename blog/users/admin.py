from django.contrib import admin

from users.models import TotalScore, User, Percent, Token


admin.site.register(TotalScore)
admin.site.register(User)
admin.site.register(Percent)
admin.site.register(Token)