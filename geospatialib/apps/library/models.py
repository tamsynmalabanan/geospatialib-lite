from django.contrib.gis.db import models
from django.utils.text import slugify
from django.db.models import Q

import shortuuid
import geojson
from urllib.parse import urlparse
import json

from . import choices

from ..utils.general import form_helpers

class MetaAbstractModel(models.Model):
    uuid = models.SlugField('UUID', unique=True, editable=False, null=True, blank=True, max_length=16)
    added_by = models.ForeignKey("main.User", verbose_name='Added by', editable=False, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='%(class)ss_added')
    updated_by = models.ForeignKey("main.User", verbose_name='Updated by', editable=False, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='%(class)ss_updated')
    added_on = models.DateTimeField('Added on', auto_now_add=True)
    updated_on = models.DateTimeField('Updated on', auto_now=True)

    class Meta:
        abstract = True

    def assign_uuid(self):
        if not self.uuid:
            while True:
                uuid = shortuuid.uuid()[:16]
                if not self.__class__.objects.filter(uuid__iexact=uuid).exists():
                    break
            self.uuid = uuid

    def save(self, *args, **kwargs):
        self.assign_uuid()
        super().save(*args, **kwargs)

class GeomAbstractModel(models.Model):
    bbox = models.PolygonField('Bounding box', blank=True, null=True)

    class Meta:
        abstract = True

class URL(MetaAbstractModel):
    path = models.URLField('URL', max_length=256, unique=True)

    def __str__(self) -> str:
        return self.path

    @property
    def domain(self):
        return urlparse(self.path).netloc
    
class Dataset(MetaAbstractModel, GeomAbstractModel):
    url = models.ForeignKey("library.URL", verbose_name='URL', on_delete=models.CASCADE)
    format = models.CharField('Format', max_length=16, choices=form_helpers.dict_to_choices(choices.DATASET_FORMATS))
    name = models.CharField('Layer', max_length=256)
    data = models.JSONField('Data', default=dict)

    class Meta:
        unique_together = ['url', 'format', 'name']

    def __str__(self) -> str:
        return self.name

    @property
    def geojson(self):
        geom_json = json.loads(self.bbox.geojson)
        feature = geojson.Feature(
            geometry=geom_json,
            properties={
                'url':self.url.path,
                'format':self.format,
                'name':self.name,
                'data':json.loads(self.data),
            },
        )
        return feature
        # return json.dumps(feature)
