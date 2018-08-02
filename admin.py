from django.contrib import admin
from .models import *


class BookmarkInline(admin.TabularInline):
	model = Bookmark
	extra = 1
	verbose_name = "bookmark"
	# ordering = ['order']
	# exclude = ("metro", "organization")


class DiscoverInline(admin.TabularInline):
	model = Discover
	extra = 1
	ordering = ['order']
	# exclude = ("metro", "organization")


class DefaultInline(admin.TabularInline):
	model = Default
	extra = 1
	ordering = ['order']
	# exclude = ("metro", "organization")


class TodoInline(admin.TabularInline):
	model = Todo
	extra = 1
	ordering = ['order']


class MetroTipInline(admin.TabularInline):
	model = Metro.tips.through
	extra = 1
	verbose_name = "tip"


class OrganizationTipInline(admin.TabularInline):
	model = Organization.tips.through
	extra = 1
	verbose_name = "tip"


@admin.register(Metro)
class MetroAdmin(admin.ModelAdmin):
	exclude = ('tips',)
	list_display = ('name', 'public')
	inlines = (DiscoverInline, DefaultInline, MetroTipInline)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
	exclude = ('tips',)
	list_display = ('name', 'metro', 'public')
	inlines = (DiscoverInline, DefaultInline, OrganizationTipInline)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
	exclude = ('next', 'ctas')
	list_display = ('name', 'metros', 'categories', 'featured')
	list_filter = ('metro', 'category')
	
	def metros(self, obj):
		return list(obj.metro.all())

	def categories(self, obj):
		return list(obj.category.all())


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'content', 'sponsor', 'public')
	def get_queryset(self, request):
		qs = super(ItemAdmin, self).get_queryset(request)
		return qs.filter(place=None)


@admin.register(ProspectiveUser)
class ProspectiveUserAdmin(admin.ModelAdmin):
	list_display = ('email', 'organization')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'metro', 'organization', 'joined', 'last_change')
	inlines = (BookmarkInline, TodoInline)


@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
	list_display = ('name', 'content')


@admin.register(Cta)
class CtaAdmin(admin.ModelAdmin):
	list_display = ('name', 'link')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
	list_display = ('name', 'items_list')
	
	def items_list(self, obj):
		return list(obj.items.all())


@admin.register(Category)
class GroupAdmin(admin.ModelAdmin):
	list_display = ('name', 'tags_list')
	
	def tags_list(self, obj):
		return list(obj.tags.all())


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	pass