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

from utils.general import form_helpers, util_helpers


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

class Map(models.Model):
    privacy = models.CharField('Privacy', max_length=8, choices=form_helpers.dict_to_choices(choices.MAP_PRIVACY), default='default')
    owner = models.ForeignKey("main.User", verbose_name='Owner', on_delete=models.CASCADE, related_name='maps')
    roles = models.ManyToManyField("main.User", 'Roles', through='library.MapRole', blank=True)

    published = models.BooleanField('Published', default=False)
    published_on = models.DateTimeField('Date published', blank=True, null=True)
    updated_on = models.DateTimeField('Updated on', auto_now=True)
    
    focus_area = models.CharField('Focus area', max_length=255, blank=True, null=True)
    references = models.ManyToManyField("library.URL", verbose_name='References', blank=True, related_name='maps')

    def __str__(self) -> str:
        return self.content.label

class MapRole(models.Model):
    map = models.ForeignKey("library.Map", verbose_name='Map', on_delete=models.CASCADE)
    user = models.ForeignKey("main.User", verbose_name='User', on_delete=models.CASCADE)
    role = models.CharField('Role', max_length=8, default='viewer', choices=form_helpers.dict_to_choices(choices.MAP_ROLES))

class Content(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    added_by = models.ForeignKey("main.User", verbose_name='Added by', editable=False, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)ss_added')
    added_on = models.DateTimeField('Added on', auto_now_add=True)
    
    updated_by = models.ForeignKey("main.User", verbose_name='Updated by', editable=False, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)ss_updated')
    updated_on = models.DateTimeField('Updated on', auto_now=True)

    type = models.CharField('Type', choices=[('dataset','dataset'), ('map', 'map')], editable=False, max_length=8, default='dataset')
    dataset = models.OneToOneField("library.Dataset", verbose_name='Dataset', on_delete=models.CASCADE, related_name='content', blank=True, null=True, editable=False)
    map = models.OneToOneField("library.Map", verbose_name='Map', on_delete=models.CASCADE, related_name='content', blank=True, null=True, editable=False)

    label = models.CharField('label', max_length=255, blank=True, null=True)
    abstract = models.TextField('Abstract', blank=True, null=True)
    tags = models.ManyToManyField("library.Tag", verbose_name='Tags', blank=True, related_name='contents')
    bbox = models.PolygonField('Bounding box', blank=True, null=True)

    def __str__(self) -> str:
        if self.label:
            return self.label
        return super().__str__()

    @property
    def instance(self):
        return getattr(self, self.type)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
