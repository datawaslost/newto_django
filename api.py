import json

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.db import models as db_models

from rest_framework import serializers, viewsets, generics, authentication, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes #, action
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_extra_fields.geo_fields import PointField

from . import models


class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ('email', 'is_staff', 'id')


class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer


class TipSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Tip
		fields = ("name", "content")


class CtaSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Cta
		exclude = ('id',)


class BookmarkSerializer(serializers.ModelSerializer):
	image = serializers.SerializerMethodField()
	place = serializers.SerializerMethodField()
	group = serializers.SerializerMethodField()
	rating = serializers.SerializerMethodField()
	distance = serializers.SerializerMethodField()
	items = serializers.SerializerMethodField()
	article = serializers.SerializerMethodField()
	
	def get_article(self, instance):
		# return true if it's an article with content
		return True if instance.content != "" and instance.content != None else False

	def get_image(self, instance):
		# returning image url if there is an image else null
		return instance.image.url if instance.image else None

	def get_place(self, instance):
		try:
			place = getattr(instance, "place")
			return True
		except:
			return False

	def get_group(self, instance):
		try:
			place = getattr(instance, "group")
			return True
		except:
			return False

	def get_rating(self, instance):
		# connect this to an average of ratings later
		return 3.0

	def get_distance(self, instance):
		# connect this to a distance calculation later
		return 1.7

	def get_items(self, instance):
		try:
			count = instance.group.items.count()
			return count
		except:
			return 0

	class Meta:
		model = models.Place
		exclude = ('next', 'phone', 'metro', 'category', 'tags', 'ratings', 'address', 'city', 'state', 'ctas', 'content', 'public', 'link', 'location')


class ItemSerializer(serializers.ModelSerializer):
	image = serializers.SerializerMethodField()
	article = serializers.SerializerMethodField()
	group = serializers.SerializerMethodField()
	items = serializers.SerializerMethodField()

	def get_group(self, instance):
		try:
			place = getattr(instance, "group")
			return True
		except:
			return False

	def get_items(self, instance):
		try:
			count = instance.group.items.count()
			return count
		except:
			return 0

	def get_article(self, instance):
		# return true if it's an article with content
		return True if instance.content != "" and instance.content != None else False
	
	def get_image(self, instance):
		# returning image url if there is an image else blank string
		return instance.image.url if instance.image else None

	class Meta:
		model = models.Item
		exclude = ('next', 'content', 'link', 'ctas', 'public')


class DiscoverSerializer(serializers.ModelSerializer):
	id = serializers.ReadOnlyField(source='item.id')
	name = serializers.ReadOnlyField(source='item.name')
	sponsor = serializers.ReadOnlyField(source='item.sponsor')
	image = serializers.SerializerMethodField()
	article = serializers.SerializerMethodField()
	group = serializers.SerializerMethodField()
	items = serializers.SerializerMethodField()

	def get_group(self, instance):
		try:
			place = getattr(instance.item, "group")
			return True
		except:
			return False

	def get_items(self, instance):
		try:
			count = instance.item.group.items.count()
			return count
		except:
			return 0

	def get_article(self, instance):
		# return true if it's an article with content
		return True if instance.item.content != "" and instance.item.content != None else False
	
	def get_image(self, instance):
		# returning image url if there is an image else blank string
		return instance.item.image.url if instance.item.image else None

	class Meta:
		model = models.Discover
		exclude = ('organization', 'item')


class TodoSerializer(DiscoverSerializer):
	content = serializers.ReadOnlyField(source='item.content')
	ctas = CtaSerializer(source='item.ctas', many=True)

	class Meta:
		model = models.Todo
		exclude = ('profile', 'item')


class FullItemSerializer(serializers.ModelSerializer):
	ctas = CtaSerializer(many=True)
	image = serializers.SerializerMethodField()
	article = serializers.SerializerMethodField()
	bookmarked = serializers.SerializerMethodField()

	def get_bookmarked(self, instance):
		# return true if this item is bookmarked by the user
		user = None
		request = self.context.get("request")
		if request and hasattr(request, "user"):
			try:
				profile = request.user.profile
				return models.Bookmark.objects.filter(item=instance, profile=profile).exists()
			except:
				return False
		return False
	
	def get_article(self, instance):
		# return true if it's an article with content
		return True if instance.content != "" and instance.content != None else False
	
	def get_image(self, instance):
		# returning image url if there is an image else blank string
		return instance.image.url if instance.image else None

	class Meta:
		model = models.Item
		exclude = ('next', 'public',)


class ItemViewSet(viewsets.ModelViewSet):
	queryset = models.Item.objects.all()
	serializer_class = FullItemSerializer


class MetroSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Metro
		fields = ('name', 'id')


class TagSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Tag
		fields = ('name', 'id')


class CategorySerializer(serializers.ModelSerializer):
	id = serializers.ReadOnlyField(source='category.id')
	name = serializers.ReadOnlyField(source='category.name')
	image = serializers.SerializerMethodField()
	tags = TagSerializer(source='category.tags', many=True)
	# tags = serializers.ReadOnlyField(source='category.tags')

	def get_image(self, instance):
		# returning image url if there is an image else blank string
		return instance.category.image.url if instance.category.image else None

	class Meta:
		model = models.OrgCategory
		fields = ('id', 'name', 'image', 'tags', 'order')


class OrganizationSerializer(serializers.ModelSerializer):
	# tips = TipSerializer(many=True)
	discover_items = serializers.SerializerMethodField()
	popular = serializers.SerializerMethodField()
	metro = MetroSerializer()
	categories = serializers.SerializerMethodField()
	nav_image = serializers.SerializerMethodField()

	def get_discover_items(self, obj):
		qset = models.Discover.objects.filter(organization=obj)
		return [DiscoverSerializer(m).data for m in qset]

	def get_categories(self, obj):
		qset = models.OrgCategory.objects.filter(organization=obj)
		return [CategorySerializer(m).data for m in qset]

	def get_nav_image(self, instance):
		# returning image url if there is an image else blank string
		return instance.nav_image.url if instance.nav_image else None

	def get_popular(self, container):
		# this needs to be a more complex algorithm for determiing popularity
		items = models.Item.objects.all().order_by('-id')[:10]
		serializer = ItemSerializer(instance=items, many=True)
		return serializer.data

	class Meta:
		model = models.Organization
		fields = ('name', 'metro', 'id', 'discover_items', 'popular', 'nav_name', 'nav_image', 'categories')


class SimpleOrganizationSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Organization
		fields = ('name', 'id')


class OrganizationViewSet(viewsets.ModelViewSet):
	queryset = models.Organization.objects.filter(public=True)
	serializer_class = SimpleOrganizationSerializer


class ProfileSerializer(serializers.ModelSerializer):
	# email = serializers.ReadOnlyField(source='user.email')
	user = UserSerializer()
	organization = OrganizationSerializer()
	bookmarks = BookmarkSerializer(many=True)
	todo = serializers.SerializerMethodField()

	def get_todo(self, obj):
		qset = models.Todo.objects.filter(profile=obj)
		return [TodoSerializer(m).data for m in qset]

	class Meta:
		model = models.Profile
		fields = ('user', 'organization', 'id', 'url', 'todo', 'bookmarks')


class ProfileViewSet(viewsets.ModelViewSet):
	queryset = models.Profile.objects.all()
	serializer_class = ProfileSerializer


class PlaceSerializer(serializers.ModelSerializer):
	# category = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
	# tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
	image = serializers.SerializerMethodField()
	rating = serializers.SerializerMethodField()
	distance = serializers.SerializerMethodField()
	location = PointField(required=False)
	bookmarked = serializers.SerializerMethodField()

	def get_bookmarked(self, instance):
		# return true if this item is bookmarked by the user
		user = None
		request = self.context.get("request")
		if request and hasattr(request, "user"):
			try:
				profile = request.user.profile
				return models.Bookmark.objects.filter(item=instance, profile=profile).exists()
			except:
				return False
		return False

	def get_image(self, instance):
		# returning image url if there is an image else null
		return instance.image.url if instance.image else None

	def get_rating(self, instance):
		# connect this to an average of ratings later
		return 3.0

	def get_distance(self, instance):
		# connect this to a distance calculation later
		return 1.7
	
	class Meta:
		model = models.Place
		exclude = ('next', 'ctas', 'ratings', 'metro', 'category', 'tags')


class PlaceViewSet(viewsets.ModelViewSet):
	queryset = models.Place.objects.all()
	serializer_class = PlaceSerializer


class GroupSerializer(serializers.ModelSerializer):
	items = ItemSerializer(many=True)
	image = serializers.SerializerMethodField()
	bookmarked = serializers.SerializerMethodField()

	def get_bookmarked(self, instance):
		# return true if this item is bookmarked by the user
		user = None
		request = self.context.get("request")
		if request and hasattr(request, "user"):
			try:
				profile = request.user.profile
				return models.Bookmark.objects.filter(item=instance, profile=profile).exists()
			except:
				return False
		return False

	def get_image(self, instance):
		# returning image url if there is an image else blank string
		return instance.image.url if instance.image else None
	
	class Meta:
		model = models.Group
		exclude = ('next', 'ctas', 'link')


class GroupViewSet(viewsets.ModelViewSet):
	queryset = models.Group.objects.all()
	serializer_class = GroupSerializer


class MeSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	organization = OrganizationSerializer()
	bookmarks = BookmarkSerializer(many=True)
	todo = serializers.SerializerMethodField()

	def get_todo(self, obj):
		qset = models.Todo.objects.filter(profile=obj)
		return [TodoSerializer(m).data for m in qset]

	class Meta:
		model = models.Profile
		fields = ('user', 'organization', 'id', 'todo', 'bookmarks', 'hometown')


class MeViewSet(viewsets.ModelViewSet):
	# authentication_classes = (JSONWebTokenAuthentication,)
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class = MeSerializer

	def get_queryset(self):
		return models.Profile.objects.filter(user=self.request.user.pk)

	
@csrf_exempt
def emailCheck(request):
	if request.method == 'POST' and request.POST.get('email', False):
		if not User.objects.filter(email=request.POST["email"]).exists():
			if models.ProspectiveUser.objects.filter(email=request.POST["email"]).exists():
				return JsonResponse({'exists': False, 'organization': models.ProspectiveUser.objects.get(email=request.POST["email"]).organization.id})
			return JsonResponse({'exists': False})
		return JsonResponse({'exists': True})
	return HttpResponse(status=400)


@csrf_exempt
def onboarding(request):
	# should this require rest-auth token authentication?
	id = request.POST.get('id', False)
	email = request.POST.get('email', False)
	hometown = request.POST.get('hometown', False)
	organization_id = request.POST.get('organization', False)
	if request.method == 'POST' and email and id:
		if User.objects.filter(email=email,id=id).exists():
			profile = models.Profile.objects.get(user=id)
			if organization_id:
				profile.organization = models.Organization.objects.get(id=organization_id)
			if hometown:
				profile.hometown = hometown
			# clear old stuff
			profile.todo.clear()
			# add default items from organization
			if profile.organization:
				for item in profile.organization.default_items.all():
					new_todo_item = models.Todo(profile=profile, item=item, order=models.Default.objects.get(organization=profile.organization, item=item).order)
					new_todo_item.save()
			profile.save()
			data = {
				'id': profile.user.id,
				'hometown': profile.hometown,
			}
			if profile.organization:
				data["organization"] = profile.organization.id
			return JsonResponse(data)
		return HttpResponse(status=404)
	return HttpResponse(status=400)
	

@api_view(['POST'])
# @authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def AddBookmark(request):
	if request.method == 'POST' and request.data["id"]:
		try: 
			item = models.Item.objects.get(id=request.data["id"])
			profile = request.user.profile
			bookmark = models.Bookmark(profile=profile, item=item)
			bookmark.save()
			return Response({"success": True, "id": request.data["id"]})
		except:
			return HttpResponse(status=400)
	return HttpResponse(status=400)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def RemoveBookmark(request):
	if request.method == 'POST' and request.data["id"]:
		try: 
			id = int(request.data["id"])
			item = models.Item.objects.get(id=id)
			profile = request.user.profile
			bookmark = models.Bookmark.objects.filter(profile=profile, item=item)
			bookmark.delete()
			return Response({"success": True, "id": id})
		except:
			return Response({"success": False, "id": int(request.data["id"]) })
	return HttpResponse(status=400)
