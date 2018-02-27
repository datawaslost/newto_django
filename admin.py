from django.contrib import admin
from .models import *

class ProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(Profile, ProfileAdmin)

admin.site.register(ProspectiveUser)
admin.site.register(School)
admin.site.register(Tip)
admin.site.register(Item)
admin.site.register(Group)
admin.site.register(Place)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Cta)

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

admin.site.register(Metro, MetroAdmin)