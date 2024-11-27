from typing import Iterable
from django.db import models
from django.utils.text import slugify
from django.db.models import Q
from django.contrib.postgres.search import SearchVectorField

import uuid
import geojson
from urllib.parse import urlparse
import json

from . import choices

from utils.general import form_helpers, util_helpers


    
    
class Dataset(models.Model):
    url = models.ForeignKey("main.URL", verbose_name='URL', on_delete=models.CASCADE, related_name='datasets')
    format = models.CharField('Format', max_length=32, choices=form_helpers.dict_to_choices(choices.DATASET_FORMATS))
    name = models.CharField('Layer', max_length=255)

    extra_data = models.JSONField('Data', blank=True, null=True)
    default_style = models.CharField('Default style name', max_length=255, blank=True, null=True)
    default_legend = models.ForeignKey("main.URL", verbose_name='Default style url', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        unique_together = ['url', 'format', 'name']

    def __str__(self) -> str:
        return self.name

