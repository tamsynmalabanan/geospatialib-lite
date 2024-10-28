from django.contrib.gis.db import models
from django.utils.text import slugify
from django.db.models import Q
from django.contrib.postgres.search import SearchVectorField

import shortuuid
import geojson
from urllib.parse import urlparse
import json

from . import choices

from utils.general import form_helpers, util_helpers



class MetaAbstractModel(models.Model):
    added_by = models.ForeignKey("main.User", verbose_name='Added by', editable=False, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='%(class)ss_added')
    updated_by = models.ForeignKey("main.User", verbose_name='Updated by', editable=False, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='%(class)ss_updated')
    added_on = models.DateTimeField('Added on', auto_now_add=True)
    updated_on = models.DateTimeField('Updated on', auto_now=True)

    class Meta:
        abstract = True

class ContentAbstractModel(models.Model):
    uuid = models.SlugField('UUID', unique=True, editable=False, null=True, blank=True, max_length=16)
    bbox = models.PolygonField('Bounding box', blank=True, null=True)
    title = models.CharField('Title', max_length=256, blank=True, null=True)
    tags = models.ManyToManyField("library.Tag", verbose_name='Tags', blank=True)

    class Meta:
        abstract = True

    def assign_uuid(self):
        if not self.uuid:
            while True:
                uuid = shortuuid.uuid()[:16]
                if not self.__class__.objects.filter(uuid__iexact=uuid).exists():
                    break
            self.uuid = uuid

    @property
    def content_geojson(self):
        geom_json = json.loads(self.bbox.geojson)
        feature = geojson.Feature(
            geometry=geom_json,
            properties={
                'uuid':self.uuid,
                'title':self.title,
            },
        )
        return feature
    
    def save(self, *args, **kwargs):
        self.assign_uuid()
        super().save(*args, **kwargs)


class Tag(models.Model):
    tag = models.CharField('Tag', max_length=256)

    def __str__(self) -> str:
        if self.tag:
            return self.tag
        return super().__str__()
    
class URL(MetaAbstractModel):
    path = models.URLField('URL', max_length=256, unique=True)
    tags = models.ManyToManyField("library.Tag", verbose_name='Tags', blank=True)

    def __str__(self) -> str:
        return self.path

    @property
    def domain(self):
        return urlparse(self.path).netloc

    def collect_tags(self):
        if self.pk and not self.tags.exists():
            tags = util_helpers.split_by_special_characters(self.path)
            tag_instances = []
            for tag in tags:
                if len(tag) > 3 and 'http' not in tag:
                    tag_instance, created = Tag.objects.get_or_create(tag=tag)
                    if tag_instance:
                        tag_instances.append(tag_instance)
            self.tags.set(tag_instances)
            self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.collect_tags()

    
class Dataset(MetaAbstractModel, ContentAbstractModel):
    url = models.ForeignKey("library.URL", verbose_name='URL', on_delete=models.CASCADE, related_name='datasets')
    format = models.CharField('Format', max_length=16, choices=form_helpers.dict_to_choices(choices.DATASET_FORMATS))
    name = models.CharField('Layer', max_length=256)
    data = models.JSONField('Data', blank=True, null=True)

    class Meta:
        unique_together = ['url', 'format', 'name']

    def __str__(self) -> str:
        return self.title

class Map(MetaAbstractModel, ContentAbstractModel):
    pass

class Content(models.Model):
    type = models.CharField('Type', choices=[('dataset','dataset'), ('map', 'map')], editable=False, max_length=8, default='dataset')
    dataset = models.OneToOneField("library.Dataset", verbose_name='Dataset', on_delete=models.CASCADE, related_name='content', blank=True, null=True)
    map = models.OneToOneField("library.Map", verbose_name='Map', on_delete=models.CASCADE, related_name='content', blank=True, null=True)

    def __str__(self) -> str:
        return getattr(self, self.type).title

    @property
    def instance(self):
        return getattr(self, self.type)

    def assign_type(self):
        if not self.pk and self.map:
            self.type = 'map'

    def save(self, *args, **kwargs):
        self.assign_type()
        super().save(*args, **kwargs)
