from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
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


class MetroSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Metro
		fields = ('name', 'public', 'id', 'url')


class MetroViewSet(viewsets.ModelViewSet):
	queryset = models.Metro.objects.all()
	serializer_class = MetroSerializer


class OrganizationSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Organization
		fields = ('name', 'metro', 'id', 'url')


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
		exclude = ('next', 'ctas', 'ratings', 'metro', 'id', 'url')


class PlaceViewSet(viewsets.ModelViewSet):
	queryset = models.Place.objects.all()
	serializer_class = PlaceSerializer