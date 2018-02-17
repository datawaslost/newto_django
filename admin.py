from django.contrib import admin
from .models import *

class ProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(Profile, ProfileAdmin)

admin.site.register(ProspectiveUser)

admin.site.register(Metro)
admin.site.register(School)
admin.site.register(Tip)
admin.site.register(Item)
admin.site.register(Group)
admin.site.register(Place)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Cta)

