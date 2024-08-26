from django.contrib import admin
from unfold.admin import ModelAdmin
from contests.models import Contest, PrizeAlbumElement, PrizePostElement, PrizeQuestElement


@admin.register(Contest)
class ContestAdmin(ModelAdmin):
    exclude = ('slug', 'is_end')
    
@admin.register(PrizeAlbumElement)
class PrizeAlbumElementAdmin(ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['contest'].queryset = Contest.objects.filter(
            criteries='assessment', 
            item_type='album',
            is_end=False
        )
        return super(PrizeAlbumElementAdmin, self).render_change_form(request, context, *args, **kwargs)
    
@admin.register(PrizePostElement)
class PrizePostElementAdmin(ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['contest'].queryset = Contest.objects.filter(
            criteries='assessment', 
            item_type='post',
            is_end=False
        )
        return super(PrizePostElementAdmin, self).render_change_form(request, context, *args, **kwargs)
    
@admin.register(PrizeQuestElement)
class PrizeQuestElementAdmin(ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['contest'].queryset = Contest.objects.filter(
            criteries='assessment', 
            item_type='quest',
            is_end=False
        )
        return super(PrizeQuestElementAdmin, self).render_change_form(request, context, *args, **kwargs)