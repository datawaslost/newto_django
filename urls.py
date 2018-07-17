from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from . import views
from . import models
from . import api


# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', api.UserViewSet)
router.register(r'profile', api.ProfileViewSet)
router.register(r'metro', api.MetroViewSet)
router.register(r'organization', api.OrganizationViewSet)
router.register(r'place', api.PlaceViewSet)
router.register(r'item', api.ItemViewSet)
router.register(r'group', api.GroupViewSet)
router.register(r'me', api.MeViewSet, base_name="me")


urlpatterns = [
	path('admin/', admin.site.urls),
	path('', views.test, name='test'),
	url(r'^api/', include(router.urls)),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
