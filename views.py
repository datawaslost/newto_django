from django.http import HttpResponse
import datetime
from . import models

def test(request):
	test_models = models.Profile.objects.all()
	now = datetime.datetime.now()
	html = "<html><body>It is now %s.</body></html>" % now
	return HttpResponse(html)