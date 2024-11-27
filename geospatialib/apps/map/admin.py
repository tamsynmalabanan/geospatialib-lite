from django.contrib import admin

from . import models

admin.site.register(models.Map)
admin.site.register(models.MapRole)
admin.site.register(models.MapReference)
admin.site.register(models.MapLog)
