from django.db.models.query import QuerySet
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.contrib import messages
from django.views.generic.list import ListView
from django.db.models import Count, Sum, F, IntegerField, Value, Q, Case, When, Max, TextField, CharField, FloatField
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, SearchHeadline
from django.utils.text import slugify
from django.contrib.gis.geos import Polygon, GEOSGeometry
from django.http import JsonResponse
from django.urls import reverse_lazy

import time

from apps.map import (
    forms as map_forms, 
    choices as map_choices, 
    models as map_models
)

from apps.library import (
    forms as lib_forms, 
    choices as lib_choices, 
    models as lib_models
)

from utils.general import form_helpers, util_helpers, model_helpers
from utils.gis import dataset_helpers
import json
import requests

@require_http_methods(['GET'])
@login_required
def tags_datalist(request):
    current_tags = request.GET.get('tags','').split(',')
    query = request.GET.get('tags_new', '').strip()

    tags_query = lib_models.Tag.objects.filter(tag__istartswith=query)
    tags_query = tags_query.exclude(tag__in=current_tags)

    tags_query = tags_query.annotate(content_count=Count('contents', distinct=True))
    tags_query = tags_query.order_by('-content_count')
    tags_query = tags_query[:5]
    
    template = 'base/components/form/datalist.html'
    return render(request, template, {'queryset': tags_query})

@require_http_methods(['POST'])
@login_required
def create_map(request):
    map_instance = None
    content_instance = None

    user = request.user

    data = request.POST.dict()
    data['owner'] = user.pk
    form = map_forms.CreateMapForm(data=data)
    
    clean_title = None
    if data.get('title', '').strip() != '':
        title_field = form['title']
        clean_title = form_helpers.validate_field(title_field)
        
    tags_field = form['tags']
    clean_tags = form_helpers.validate_field(tags_field)
    if clean_tags:
        form.data.update({'tags':clean_tags})
    else:
        form.data.update({'tags':''})
        if not clean_title:
            form_helpers.remove_classes_from_field(tags_field, ['is-invalid'])

    focus_area_value = data.get('focus_area', '').strip()
    if focus_area_value != '':
        form.data.update({'focus_area': focus_area_value.title()})

    if data.get('submit') is not None:
        if form.is_valid():
            clean_data = form.cleaned_data
            map_instance = map_models.Map.objects.create(
                owner=user, 
                focus_area=clean_data.get('focus_area', '')
            )
            if map_instance:
                content_instance = lib_models.Content.objects.create(
                    added_by=user,
                    type='map',
                    map=map_instance,
                    label=clean_data.get('title', ''),
                    bbox=clean_data.get('bbox', ''),
                )
                if content_instance:
                    tag_instances = model_helpers.list_to_tags(clean_data.get('tags','').split(','))
                    content_instance.tags.set(tag_instances)

                    messages.success(request, 'Map successfully created!', 'map-floating-message')
                    response = HttpResponse()
                    response['HX-Redirect'] = reverse_lazy('map:index', kwargs={'pk': content_instance.pk})
                    return response

        
        if not map_instance or not content_instance:
            messages.error(request, 'There was an error while creating the map. Please review the form and try again.', 'create-map-form')

    return render(request, 'library/create_map/form.html', {'form':form, 'content':content_instance})

@login_required
def map_privacy(request):
    map_instance = get_object_or_404(map_models.Map, content__pk=request.GET.get('uuid'))

    context_data = request.GET.get('context', '{}')
    context = json.loads(context_data)
    context['map'] = map_instance

    return render(request, 'library/map/privacy.html', context)

