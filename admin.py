from django.contrib import admin
from .models import *


class DiscoverInline(admin.TabularInline):
	model = Discover
	extra = 1
	ordering = ['order']


class DefaultInline(admin.TabularInline):
	model = Default
	extra = 1
	ordering = ['order']


class TipInline(admin.TabularInline):
	model = Metro.tips.through
	extra = 1
	verbose_name = "tip"

    
class MetroAdmin(admin.ModelAdmin):
	exclude = ('tips',)
	inlines = (DiscoverInline, DefaultInline, TipInline)


class PlaceAdmin(admin.ModelAdmin):
	exclude = ('next',)


admin.site.register(Metro, MetroAdmin)
admin.site.register(Place, PlaceAdmin)

admin.site.register(Profile)
admin.site.register(ProspectiveUser)
admin.site.register(Organization)
admin.site.register(Tip)
admin.site.register(Item)
admin.site.register(Group)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Cta)
