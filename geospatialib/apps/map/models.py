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

class Map(models.Model):
    owner = models.ForeignKey("main.User", verbose_name='Owner', on_delete=models.CASCADE, related_name='maps')
    owner_since = models.DateTimeField('Owner since', auto_now_add=True, blank=True, null=True)
    
    privacy = models.CharField('Privacy', max_length=8, choices=form_helpers.dict_to_choices(choices.MAP_PRIVACY), default='default')
    privacy_changed = models.DateTimeField('Date privacy changed', blank=True, null=True)

    published = models.BooleanField('Published', default=False)
    published_on = models.DateTimeField('Date published', blank=True, null=True)
    published_off = models.DateTimeField('Date unpublished', blank=True, null=True)
    
    updated_on = models.DateTimeField('Updated on', auto_now=True)
    
    focus_area = models.CharField('Focus area', max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return self.content.label
    
    @property
    def proper_privacy(self):
        if self.privacy == 'default':
            return choices.MAP_PRIVACY.get(self.owner.map_privacy)
        return choices.MAP_PRIVACY.get(self.privacy)
    
    def get_role(self, user):
        if self.owner == user:
            return 4
        else:
            try:
                return self.roles.get(map=self, user=user).role
            except:
                return 0
        
    def create_logs(self):
        print(vars(self))
    
    def save(self, *args, **kwargs):
        self.create_logs()
        super().save(*args, **kwargs)

# class MapReference(models.Model):
#     map = models.ForeignKey("map.Map", verbose_name='Map', on_delete=models.CASCADE, related_name='references')
#     url = models.ForeignKey("main.URL", verbose_name='URL', on_delete=models.CASCADE)
#     label = models.CharField('Label', max_length=255)

# class MapRole(models.Model):
#     map = models.ForeignKey("map.Map", verbose_name='Map', on_delete=models.CASCADE, related_name='roles')
#     user = models.ForeignKey("main.User", verbose_name='User', on_delete=models.CASCADE)
#     added_on = models.DateTimeField('Added on', auto_now_add=True, blank=True, null=True)
#     updated_on = models.DateTimeField('Updated on', auto_now=True, blank=True, null=True)
#     role = models.SmallIntegerField('Role', default=2, choices=form_helpers.dict_to_choices(choices.MAP_ROLES))

#     class Meta:
#         unique_together = ['map', 'user']

# class MapLog(models.Model):
#     map = models.ForeignKey("map.Map", verbose_name='Map', on_delete=models.CASCADE, related_name='logs')
#     user = models.ForeignKey("main.User", verbose_name='User', on_delete=models.SET_NULL, blank=True, null=True)
#     added_on = models.DateTimeField('Added on', auto_now_add=True, blank=True, null=True)
#     field = models.CharField('Field', max_length=50)
#     value = models.TextField('Value')