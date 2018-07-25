from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token

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
# router.register(r'emailcheck', api.emailCheck, base_name="emailcheck")


urlpatterns = [
	path('admin/', admin.site.urls),
	path('', views.test, name='test'),
	url(r'^api/', include(router.urls)),
	url(r'^api/emailcheck/', api.emailCheck, name='emailcheck'),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^refresh-token/', refresh_jwt_token),
    url(r'^token-verify/', verify_jwt_token),
]
