from django.contrib import admin

from . import models



admin.site.register(models.Dataset)
admin.site.register(models.URL)
admin.site.register(models.Tag)

class MetaAbstractAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id',
        'type',
        'dataset',
        'map',
        'added_by',
        'updated_by',
        'added_on',
        'updated_on',
    )
    search_fields = ['label']
    list_filter = ['type']

admin.site.register(models.Content, MetaAbstractAdmin)