from typing import Iterable
from django.contrib.gis.db import models
from django.utils.text import slugify
from django.db.models import Q
from django.contrib.postgres.search import SearchVectorField
import uuid
import geojson
from urllib.parse import urlparse
import json

from . import choices
from apps.map.models import MapLogAbstract
from utils.general import form_helpers, util_helpers
    
    
class Dataset(models.Model):
    url = models.ForeignKey("library.URL", verbose_name='URL', on_delete=models.CASCADE, related_name='datasets')
    format = models.CharField('Format', max_length=32, choices=form_helpers.dict_to_choices(choices.DATASET_FORMATS))
    name = models.CharField('Layer', max_length=255)

    extra_data = models.JSONField('Data', blank=True, null=True)
    default_style = models.CharField('Default style name', max_length=255, blank=True, null=True)
    default_legend = models.ForeignKey("library.URL", verbose_name='Default style url', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        unique_together = ['url', 'format', 'name']

    def __str__(self) -> str:
        return self.name

class Tag(models.Model):
    tag = models.CharField('Tag', max_length=64, unique=True)

    def __str__(self) -> str:
        return self.tag
    
    def save(self, *args, **kwargs):
        self.tag = self.tag.lower()
        super().save(*args, **kwargs)

class URL(models.Model):
    url = models.URLField('URL', max_length=255, unique=True)

    def __str__(self) -> str:
        return self.url

    @property
    def domain(self):
        return urlparse(self.url).netloc
    
class Content(MapLogAbstract):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        
    type = models.CharField('Type', choices=[('dataset','dataset'), ('map', 'map')], editable=False, max_length=8, default='dataset')
    dataset = models.OneToOneField("library.Dataset", verbose_name='Dataset', on_delete=models.CASCADE, related_name='content', blank=True, null=True, editable=False)
    map = models.OneToOneField("map.Map", verbose_name='Map', on_delete=models.CASCADE, related_name='content', blank=True, null=True, editable=False)

    title = models.CharField('Title', max_length=255, blank=True, null=True)
    abstract = models.TextField('Abstract', blank=True, null=True)
    tags = models.ManyToManyField("library.Tag", verbose_name='Tags', blank=True, related_name='contents')
    bbox = models.PolygonField('Bounding box', blank=True, null=True)

    def __str__(self) -> str:
        if self.title:
            return self.title
        return super().__str__()

    @property
    def instance(self):
        return getattr(self, self.type)