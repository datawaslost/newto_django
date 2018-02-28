from . import models
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = models.Profile
		fields = ('user', 'metro')


class ProfileViewSet(viewsets.ModelViewSet):
	queryset = models.Profile.objects.all()
	serializer_class = ProfileSerializer


class MetroSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = models.Metro
		fields = ('name', 'public')


class MetroViewSet(viewsets.ModelViewSet):
	queryset = models.Metro.objects.all()
	serializer_class = MetroSerializer