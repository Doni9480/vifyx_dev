from django.contrib import admin

from users.models import TotalScore, User, Percent, Token, Percent_for_content


admin.site.register(TotalScore)
admin.site.register(User)
admin.site.register(Percent)
admin.site.register(Token)
admin.site.register(Percent_for_content)