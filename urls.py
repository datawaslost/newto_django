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

router.register(r'me', api.MeViewSet, base_name="me")
router.register(r'organization', api.OrganizationViewSet)

# these should likely be removed for production
# router.register(r'users', api.UserViewSet)
router.register(r'profile', api.ProfileViewSet)
router.register(r'place', api.PlaceViewSet)
router.register(r'item', api.ItemViewSet)
router.register(r'group', api.GroupViewSet)


urlpatterns = [
	path('admin/', admin.site.urls),
	path('', views.test, name='test'),
	url(r'^api/', include(router.urls)),
	
	url(r'^api/emailcheck/', api.emailCheck, name='emailcheck'),
	url(r'^api/passwordcheck/', api.passwordCheck, name='passwordcheck'),
	url(r'^api/onboarding/', api.onboarding, name='onboarding'),
	url(r'^api/addbookmark/', api.AddBookmark, name='addbookmark'),
	url(r'^api/removebookmark/', api.RemoveBookmark, name='removebookmark'),
	url(r'^api/adddone/', api.AddDone, name='adddone'),
	url(r'^api/removedone/', api.RemoveDone, name='removedone'),
	url(r'^api/addlist/', api.AddList, name='addlist'),
	url(r'^api/removelist/', api.RemoveList, name='removelist'),
	url(r'^api/addrating/', api.AddRating, name='addrating'),
	url(r'^api/location/', api.Location, name='location'),

	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^refresh-token/', refresh_jwt_token),
    url(r'^token-verify/', verify_jwt_token),
]
