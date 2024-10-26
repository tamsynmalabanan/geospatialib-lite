from django.contrib import admin

from . import models

class MetaAbstractAdmin(admin.ModelAdmin):
    readonly_fields = (
        # 'uuid',
        'added_by',
        'updated_by',
        'added_on',
        'updated_on',
    )

admin.site.register(models.URL, MetaAbstractAdmin)
admin.site.register(models.Dataset, MetaAbstractAdmin)
admin.site.register(models.Content)