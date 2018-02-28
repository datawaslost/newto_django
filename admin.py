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


@admin.register(Metro)
class MetroAdmin(admin.ModelAdmin):
	exclude = ('tips',)
	inlines = (DiscoverInline, DefaultInline, TipInline)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
	exclude = ('next',)
	list_display = ('name', 'metro', 'category', 'featured')
    list_filter = ('metro', 'category')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
	def queryset(self, request):
		qs = super(ItemAdmin, self).queryset(request)
		qs.filter(place=None)
		return qs


admin.site.register(Profile)
admin.site.register(ProspectiveUser)
admin.site.register(Organization)
admin.site.register(Tip)
admin.site.register(Group)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Cta)
