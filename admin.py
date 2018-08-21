from django.contrib import admin

# from openinghours.admin import OpeningHoursInline, ClosingRulesInline

from .models import *

from openinghours.models import OpeningHours, ClosingRules, Company


class OpeningHoursInline(admin.TabularInline):
	model = OpeningHours
	extra = 0


class ClosingRulesInline(admin.StackedInline):
	model = ClosingRules
	extra = 0



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


class OrganizationTipInline(admin.TabularInline):
	model = Organization.tips.through
	extra = 1
	verbose_name = "tip"


class CategoryInline(admin.TabularInline):
	model = Organization.categories.through
	extra = 1
	verbose_name = "category"
	ordering = ['order']


@admin.register(Metro)
class MetroAdmin(admin.ModelAdmin):
	list_display = ('name',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
	list_display = ('profile','place','rating')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
	exclude = ('tips',)
	list_display = ('name', 'metro', 'public')
	inlines = (DiscoverInline, DefaultInline, OrganizationTipInline, CategoryInline)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
	exclude = ('next', 'ctas')
	list_display = ('name', 'metros', 'categories', 'featured')
	list_filter = ('metro', 'category')
	inlines = [OpeningHoursInline, ClosingRulesInline]

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
	list_display = ('user', 'organization', 'joined', 'last_change')
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