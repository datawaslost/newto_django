from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, generics
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
	default_items = ItemSerializer(many=True)
	discover_items = ItemSerializer(many=True)
	class Meta:
		model = models.Metro
		fields = ('name', 'public', 'id', 'url', 'default_items', 'discover_items', 'tips')


class MetroViewSet(viewsets.ModelViewSet):
	queryset = models.Metro.objects.all()
	serializer_class = MetroSerializer


class OrganizationSerializer(serializers.ModelSerializer):
	tips = TipSerializer(many=True)
	default_items = ItemSerializer(many=True)
	discover_items = ItemSerializer(many=True)
	class Meta:
		model = models.Organization
		fields = ('name', 'metro', 'id', 'url', 'default_items', 'discover_items', 'tips')


class OrganizationViewSet(viewsets.ModelViewSet):
	queryset = models.Organization.objects.all()
	serializer_class = OrganizationSerializer


class ProfileSerializer(serializers.ModelSerializer):
	# email = serializers.ReadOnlyField(source='user.email')
	user = UserSerializer()
	metro = MetroSerializer()
	organization = OrganizationSerializer()
	class Meta:
		model = models.Profile
		fields = ('user', 'metro', 'organization', 'id', 'url')


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
	# email = serializers.ReadOnlyField(source='user.email')
	user = UserSerializer()
	metro = MetroSerializer()
	organization = OrganizationSerializer()
	todo = ItemSerializer(many=True)
	bookmarks = ItemSerializer(many=True)
	class Meta:
		model = models.Profile
		fields = ('user', 'metro', 'organization', 'id', 'url', 'todo', 'bookmarks')


class MeViewSet(viewsets.ModelViewSet):
	def get_queryset(self):
		return models.Profile.objects.filter(user=self.request.user)
	serializer_class = MeSerializer

