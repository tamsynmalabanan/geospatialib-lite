from . import util_helpers
from apps.library import models as lib_models
from django.db.models import Q

def get_map_privacy_filters(user, map_field_name=None):
    queries = Q()

    prefix = ''
    if map_field_name:
        prefix = f'{map_field_name}__'

    # if not user.is_staff:
    queries = Q(**{f'{prefix}published':True}) & (
        Q(**{f'{prefix}privacy':'public'}) | Q(
            **{f'{prefix}privacy':'default'}, 
            **{f'{prefix}owner__map_privacy':'public'}
        )
    )
    
    if user.is_authenticated:
        user_pk = user.pk
        queries |= (
            Q(**{f'{prefix}content__added_by__pk':user_pk})
            | Q(**{f'{prefix}owner__pk':user_pk})
            | Q(**{f'{prefix}roles__user__pk':user_pk})
        )

    return queries

def collect_url_tags(url):
    tag_instances = []

    tags = util_helpers.split_by_special_characters(url, ['_', '-'])
    for tag in [tag for tag in tags if len(tag) > 3 and 'http' not in tag]:
        tag_instance, created = lib_models.Tag.objects.get_or_create(tag=tag.lower())
        if tag_instance:
            tag_instances.append(tag_instance)
    
    return tag_instances

def list_to_tags(tags_list):
    tag_instances = []

    for value in tags_list:
        tags = util_helpers.split_by_special_characters(value, ['_', '-'])
        for tag in tags:
            tag_instance, created = lib_models.Tag.objects.get_or_create(tag=tag.lower())
            if tag_instance:
                tag_instances.append(tag_instance)

    return tag_instances