from typing import Iterable
from django.contrib.gis.db import models
from django.utils.text import slugify
from django.db.models import Q
from django.contrib.postgres.search import SearchVectorField
from django.forms.models import model_to_dict
from django.db.models.fields.related import ManyToManyField, ManyToOneRel, OneToOneRel
from django.contrib.gis.geos.polygon import Polygon, GEOSGeometry

import uuid
import geojson
from urllib.parse import urlparse
import json
import datetime 

from . import choices
from apps.library.models import ContentLogAbstract

from utils.general import form_helpers, util_helpers

class Map(ContentLogAbstract):
    owner = models.ForeignKey("main.User", verbose_name='Owner', on_delete=models.CASCADE, related_name='maps')
    owner_since = models.DateTimeField('Owner since', blank=True, null=True)
    
    privacy = models.CharField('Privacy', max_length=8, choices=form_helpers.dict_to_choices(choices.MAP_PRIVACY), default='default')
    privacy_changed = models.DateTimeField('Date privacy changed', blank=True, null=True)

    published = models.BooleanField('Publication status', default=False)
    published_on = models.DateTimeField('Date published', blank=True, null=True)
    published_off = models.DateTimeField('Date unpublished', blank=True, null=True)
    
    focus_area = models.CharField('Focus area', max_length=255, blank=True, null=True)

    @property
    def proper_privacy(self):
        if self.privacy == 'default':
            return choices.MAP_PRIVACY.get(self.owner.map_privacy)
        return choices.MAP_PRIVACY.get(self.privacy)
        
    @property
    def contributors_dict(self):
        contributors = self.contributors.select_related('user').all()
        contributors_dict = {
            'Admins': [role for role in contributors if role.role == 3],
            'Editors': [role for role in contributors if role.role == 2],
            'Reviewers': [role for role in contributors if role.role == 1]
        }
        return contributors_dict

    def get_role(self, user):
        if self.owner == user:
            return 4
        else:
            try:
                return self.contributors.get(map=self, user=user).role
            except:
                return 0

        
class MapReference(ContentLogAbstract):
    map = models.ForeignKey("map.Map", verbose_name='Map', on_delete=models.CASCADE, related_name='references')
    url = models.ForeignKey("library.URL", verbose_name='URL', on_delete=models.CASCADE)
    label = models.CharField('Label', max_length=255)
    order = models.PositiveSmallIntegerField('Order', default=0)

    class Meta:
        unique_together = ['map', 'url']
        ordering = ['order', 'id']

    def __str__(self):
        return self.html_format

    @property
    def html_format(self):
        return f'{self.label} @ <a class="text-reset text-decoration-none" href="{self.url}" target="_blank">{self.url.domain}</a>'

class MapContributor(ContentLogAbstract):
    map = models.ForeignKey("map.Map", verbose_name='Map', on_delete=models.CASCADE, related_name='contributors')
    user = models.ForeignKey("main.User", verbose_name='User', on_delete=models.CASCADE)
    role = models.SmallIntegerField('Role', default=2, choices=form_helpers.dict_to_choices(choices.MAP_ROLES))

    class Meta:
        unique_together = ['map', 'user']
        ordering = ['-role']

    def __str__(self) -> str:
        return self.user.proper_name

    @property
    def proper_role(self):
        return choices.MAP_ROLES.get(self.role)    
