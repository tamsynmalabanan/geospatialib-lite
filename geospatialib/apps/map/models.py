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

from utils.general import form_helpers, util_helpers

class MapLogAbstract(models.Model):
    added_by = models.ForeignKey("main.User", verbose_name='Added by', editable=False, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)ss_added')
    updated_by = models.ForeignKey("main.User", verbose_name='Updated by', editable=False, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)ss_updated')
    added_on = models.DateTimeField('Added on', auto_now_add=True, blank=True, null=True)
    updated_on = models.DateTimeField('Updated on', auto_now=True, blank=True, null=True)
    
    class Meta:
        abstract = True

    @property
    def map_instance(self):
        if isinstance(self, Map):
            return self
        elif hasattr(self, 'map') and isinstance(getattr(self, 'map'), Map):
            return getattr(self, 'map')
        else:
            return None

    @property
    def log_excuded_field_exps_on_init(self):
        return [
            'owner',
            'privacy',
            'published',
            'content__label',
        ]

    @property
    def log_excluded_fields(self):
        return [
            'added_by',
            'added_on',
            'updated_by',
            'updated_on',
        ]

    @property
    def log_excluded_field_exps(self):
        return [
            'content__type',
            'content__map',
        ]

    def get_latest_field_value(self, field):
        new = getattr(self, field.name)
        if isinstance(field, ManyToManyField):
            if new.exists():
                new = list(new.all())
            else:
                new = None
        return new

    def serialize_value_for_log(self, value):
        if hasattr(value, 'pk'):
            return value.pk
        
        try:
            return json.dumps(value)
        except TypeError:
            if isinstance(value, GEOSGeometry):
                return value.geojson
            elif isinstance(value, datetime.datetime):
                return str(value)
            else:
                print(type(value), str(value))
            return str(value)

    def get_map_log_actions(self, field, current, new):
        if isinstance(field, ManyToManyField):
            actions = []

            if not current:
                current = []

            if not new:
                new = []

            removed_instances = [i for i in current if i not in new]
            for i in removed_instances:
                actions.append(('removed', i))

            added_instances = [i for i in new if i not in current]
            for i in added_instances:
                actions.append(('added', i))

            return actions
        else:
            if not current and new:
                return [('set', new)]
            elif current and not new:
                return [('removed', current)]
            elif current and new:
                return [('changed', new)]

    def get_map_log_remark(self, field, verbose_name, action, value):
        if isinstance(field, models.TextField) or isinstance(value, GEOSGeometry):
            return f'{action} {verbose_name}.'
        else:
            value_str = value
            if hasattr(field, '_choices'):
                choices = getattr(field, '_choices')
                if choices and len(choices) > 0:
                    for choice in choices:
                        if choice[0] == value:
                            value_str = choice[1]

            if isinstance(value, str):
                value_str = f'"{value_str}"'
            value_str = f'<b>{value_str}</b>'

            if action == 'set':
                return f'{action} {verbose_name} as {value_str}.'
            if action == 'removed':
                return f'{action} {value_str} from {verbose_name}.'
            if action == 'changed':
                return f'{action} {verbose_name} to {value_str}.'
            if action == 'added':
                return f'{action} {value_str} to {verbose_name}.'

    def create_logs(self, current_values={}):
        map_instance = self.map_instance
        if map_instance:
            is_init = current_values.get('id', None) is None

            model_class = self.__class__
            model_name = model_class._meta.verbose_name

            prefix = ''
            if self != map_instance:
                map_field = model_class._meta.get_field('map')
                related_name = map_field._related_name
                prefix = f'{related_name}__'
                
                related_field = Map._meta.get_field(related_name)
                if (
                    isinstance(map_field, models.ForeignKey) 
                    and isinstance(related_field, models.ManyToOneRel) 
                    and not isinstance(related_field, OneToOneRel)
                ):
                    if not current_values.get('id', None):
                        remark = f'added <b>{self}</b> to {model_class._meta.verbose_name_plural}'
                        MapLog.objects.create(
                            map=map_instance,
                            added_by=self.updated_by,
                            field_exp=related_name,
                            value=self.serialize_value_for_log(self),
                            action='added',
                            remark=remark,
                        )
                        return
                    else:
                        model_name = f"{model_name} {self}'s"
            else:
                if is_init:
                    MapLog.objects.create(
                        map=map_instance,
                        added_by=self.updated_by,
                        field_exp='id',
                        value=self.pk,
                        action='created',
                        remark=f'created this map.',
                    )

            fields = model_class._meta.fields + model_class._meta.many_to_many
            for field in fields:
                if not field.primary_key:
                    field_name = field.name
                    field_exp = f'{prefix}{field_name}'
                    if (
                        field_name not in self.log_excluded_fields 
                        and field_exp not in self.log_excluded_field_exps
                        and (not is_init or (
                            is_init and field_exp not in self.log_excuded_field_exps_on_init
                        ))
                    ):
                        current = current_values.get(field_name, None)
                        new = self.get_latest_field_value(field)

                        if current != new and (
                            not hasattr(new, 'pk') 
                            or (hasattr(new, 'pk') and current != new.pk)
                        ):
                            verbose_name = f'{model_name} {field.verbose_name.lower()}'
                            actions = self.get_map_log_actions(field, current, new)
                            if actions and len(actions) > 0:
                                for i in actions:
                                    action, value = i
                                    serialized_value = self.serialize_value_for_log(value)
                                    remark = self.get_map_log_remark(field, verbose_name, *i)
                                    MapLog.objects.create(
                                        map=map_instance,
                                        added_by=self.updated_by,
                                        field_exp=field_exp,
                                        value=serialized_value,
                                        action=action,
                                        remark=remark,
                                    )
    
class Map(MapLogAbstract):
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

        
class MapReference(MapLogAbstract):
    map = models.ForeignKey("map.Map", verbose_name='Map', on_delete=models.CASCADE, related_name='references')
    url = models.ForeignKey("library.URL", verbose_name='URL', on_delete=models.CASCADE)
    label = models.CharField('Label', max_length=255)

class MapContributor(MapLogAbstract):
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

class MapLog(models.Model):
    map = models.ForeignKey("map.Map", verbose_name='Map', on_delete=models.CASCADE, related_name='logs')
    added_by = models.ForeignKey("main.User", verbose_name='Added by', on_delete=models.SET_NULL, blank=True, null=True)
    added_on = models.DateTimeField('Added on', auto_now_add=True)
    field_exp = models.CharField('Field', max_length=32)
    value = models.TextField('Value')
    action = models.CharField('Action', max_length=8, choices=form_helpers.dict_to_choices(choices.MAP_LOG_ACTIONS), blank=True, null=True)
    remark = models.CharField('Remark', max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-added_on']

    def __str__(self) -> str:
        return self.remark
    
