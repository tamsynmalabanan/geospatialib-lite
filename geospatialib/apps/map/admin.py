from django.contrib import admin

from . import models

admin.site.register(models.Map)
admin.site.register(models.MapContributor)
admin.site.register(models.MapReference)
