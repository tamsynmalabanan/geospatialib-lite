from django.contrib import admin

from . import models

class UserAdmin(admin.ModelAdmin):
    readonly_fields = (
        'joined_on',
    )

admin.site.register(models.User, UserAdmin)

