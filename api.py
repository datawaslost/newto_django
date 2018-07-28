import json
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from rest_framework import serializers, viewsets, generics, authentication, permissions
from rest_framework.decorators import api_view #, action
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from . import models


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ('username', 'email', 'is_staff', 'id', 'url')


# ViewSets define the view behavior.
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


class ItemSerializer(serializers.ModelSerializer):
	ctas = CtaSerializer(many=True)
	class Meta:
		model = models.Item
		exclude = ('next',)


class ItemViewSet(viewsets.ModelViewSet):
	queryset = models.Item.objects.all()
	serializer_class = ItemSerializer


class MetroSerializer(serializers.ModelSerializer):
	tips = TipSerializer(many=True)
	discover_items = ItemSerializer(many=True)
	class Meta:
		model = models.Metro
		fields = ('name', 'public', 'id', 'url', 'discover_items', 'tips')


class MetroViewSet(viewsets.ModelViewSet):
	queryset = models.Metro.objects.all()
	serializer_class = MetroSerializer


class OrganizationSerializer(serializers.ModelSerializer):
	tips = TipSerializer(many=True)
	discover_items = ItemSerializer(many=True)
	class Meta:
		model = models.Organization
		fields = ('name', 'metro', 'id', 'url', 'discover_items', 'tips')


class OrganizationViewSet(viewsets.ModelViewSet):
	queryset = models.Organization.objects.all()
	serializer_class = OrganizationSerializer


class ProfileSerializer(serializers.ModelSerializer):
	# email = serializers.ReadOnlyField(source='user.email')
	user = UserSerializer()
	metro = MetroSerializer()
	organization = OrganizationSerializer()
	todo = ItemSerializer(many=True)
	class Meta:
		model = models.Profile
		fields = ('user', 'metro', 'organization', 'id', 'url', 'todo')


class ProfileViewSet(viewsets.ModelViewSet):
	queryset = models.Profile.objects.all()
	serializer_class = ProfileSerializer


class PlaceSerializer(serializers.ModelSerializer):
	category = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
	tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
	class Meta:
		model = models.Place
		exclude = ('next', 'ctas', 'ratings', 'metro')


class PlaceViewSet(viewsets.ModelViewSet):
	queryset = models.Place.objects.all()
	serializer_class = PlaceSerializer


class GroupSerializer(serializers.ModelSerializer):
	items = ItemSerializer(many=True)
	class Meta:
		model = models.Group
		exclude = ('next', 'ctas', 'link')


class GroupViewSet(viewsets.ModelViewSet):
	queryset = models.Group.objects.all()
	serializer_class = GroupSerializer


class MeSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	metro = MetroSerializer()
	organization = OrganizationSerializer()
	todo = ItemSerializer(many=True)
	bookmarks = ItemSerializer(many=True)
	class Meta:
		model = models.Profile
		fields = ('user', 'metro', 'organization', 'id', 'url', 'todo', 'bookmarks', 'hometown')


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
	metro_id = request.POST.get('metro', False)
	organization_id = request.POST.get('organization', False)
	if request.method == 'POST' and email and id:
		if User.objects.filter(email=email,id=id).exists():
			profile = models.Profile.objects.get(user=id)
			if organization_id:
				profile.organization = models.Organization.objects.get(id=organization_id)
				profile.metro = profile.organization.metro
			elif metro_id:
				profile.organization = None
				profile.metro = models.Metro.objects.get(id=metro_id)
			if hometown:
				profile.hometown = hometown
			# clear old stuff
			profile.todo.clear()
			# add default items from organization and metro
			if profile.organization:
				for item in profile.organization.default_items.all():
					new_todo_item = models.Todo(profile=profile, item=item, order=models.Default.objects.get(organization=profile.organization, item=item).order)
					new_todo_item.save()
			if profile.metro:
				for item in profile.metro.default_items.all():
					new_todo_item = models.Todo(profile=profile, item=item, order=models.Default.objects.get(metro=profile.metro, item=item).order)
					new_todo_item.save()
			profile.save()
			data = {
				'id': profile.user.id,
				'hometown': profile.hometown,
			}
			if profile.metro:
				data["metro"] = profile.metro.id
			if profile.organization:
				data["organization"] = profile.organization.id
			return JsonResponse(data)
		return HttpResponse(status=404)
	return HttpResponse(status=400)

