from django.db.models.query import QuerySet
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, HttpResponse
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

from apps.library import (
    forms as lib_forms, 
    choices as lib_choices, 
    models as lib_models
)
from utils.general import form_helpers, util_helpers, model_helpers
from utils.gis import dataset_helpers
import json
import requests

# https://medium.com/@mikyrola8/understanding-lazy-fetching-in-django-a-deep-dive-8159c4822cd4
class SearchList(ListView):
    template_name = 'library/search/results.html'
    model = lib_models.Content
    context_object_name = 'contents'
    paginate_by = 20

    @property
    def page(self):
        return int(self.request.GET.get('page', 1))

    @property
    def query(self):
        query = self.request.GET.get('query')
        
        if query.endswith('?'):
            query = query[:-1]

        return query

    @property
    def filter_fields(self):
        return [
            'type', 
            'dataset__format',
            # 'map__privacy',
            # 'map__published',
        ]

    @property
    def filter_expressions(self):
        return ['bbox__bboverlaps']

    @property
    def filters(self):
        return self.filter_fields + self.filter_expressions

    @property
    def cache_key(self):
        return util_helpers.build_cache_key(
            'search-queryset',
            self.query
        )

    def apply_privacy_filters(self, queryset):
        return queryset.filter(
            Q(type='dataset') | (
                Q(type='map') & 
                model_helpers.get_map_privacy_filters(self.request.user, 'map')
            )
        )

    def apply_query_filters(self, queryset):
        return queryset.filter(**{
            param:value 
            for param,value in self.request.GET.items() 
            if param in self.filters
            and value not in ['', None]
        })

    def perform_full_text_search(self):
        query = self.query
        if query:
            queryset = super().get_queryset()
            
            search_query = SearchQuery(query, search_type="plain")

            search_vector = SearchVector('type')
            for field in [
                'label',
                'abstract',
                'tags__tag',

                'dataset__url__url',
                'dataset__format',
                'dataset__name',
                
                'map__focus_area',
                'map__references__url',
            ]:
                search_vector = search_vector + SearchVector(field)


            # search_headline = SearchHeadline('abstract', search_query)

            queryset = (
                queryset
                .select_related(
                    'dataset', 
                    'dataset__url', 
                    'dataset__default_legend', 
                    
                    'map',
                    'map__owner',
                )
                .prefetch_related(
                    'tags', 
                    'map__roles__user',
                    # 'map__references',
                )
                .values(*self.filter_fields+[
                    'map__published', 
                    'map__privacy', 
                     
                    'added_by__pk',
                    'map__owner__pk', 
                    'map__roles__user__pk',

                    'pk', 
                    'label', 
                    'bbox',     

                    'dataset__url__url', 
                    'dataset__name', 
                    'dataset__default_style', 
                    'dataset__default_legend__url', 

                    'map__focus_area',
                    # 'map__references__url', 
                ])
                .annotate(
                    rank=SearchRank(search_vector, search_query),
                    # headline=search_headline,
                )
                .filter(rank__gte=0.001)
            )

            cache.set(self.cache_key, queryset, timeout=3600)
            return queryset

    def get_queryset(self):
        if not hasattr(self, 'queryset') or getattr(self, 'queryset') is None:
            queryset = cache.get(self.cache_key)

            if not queryset:
                queryset = self.perform_full_text_search()

            if queryset.exists():
                cache.set(self.cache_key, queryset, timeout=3600)
                queryset = self.apply_privacy_filters(queryset)
                queryset = self.apply_query_filters(queryset)

            self.queryset = queryset

        queryset = self.queryset
        if queryset and queryset.exists():
            queryset = (
                self.queryset
                .annotate(rank=Max('rank'))
                .order_by(*['-rank']+self.filter_fields+['label'])
            )
        return queryset

    def get_filters(self):
        return {
            field: (
                self.queryset
                .values(field)
                .annotate(count=Count('id', distinct=True))
                .order_by('-count')
            )
            for field in self.filter_fields
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.page == 1:
            context['filters'] = self.get_filters()
        return context



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
    form = lib_forms.CreateMapForm(data=data)
    
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
            map_instance = lib_models.Map.objects.create(
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
                    response['HX-Redirect'] = reverse_lazy('library:map', kwargs={'pk': content_instance.pk})
                    return response

        
        if not map_instance or not content_instance:
            messages.error(request, 'There was an error while creating the map. Please review the form and try again.', 'create-map-form')

    return render(request, 'library/create_map/form.html', {'form':form, 'content':content_instance})


@require_http_methods(['POST'])
@login_required
def share_dataset(request):
    user = request.user
    dataset_instance = None
    
    form = lib_forms.ShareDatasetForm(data={})
    
    data = request.POST.dict()
    url_value = data.get('url', '')
    if url_value.strip() != '':
        url_field = form['url']
        form.data.update({'url':url_value})
        clean_url = form_helpers.validate_field(url_field)
        if clean_url:
            format_field = form['format']
            format_field.field.widget.attrs['disabled'] = False

            format_value = data.get('format', '')
            if format_value == '':
                format_value = dataset_helpers.get_dataset_format(url_value)
            if format_value:
                form.data.update({'format': format_value})
                form.full_clean()
            
            clean_format = form_helpers.validate_field(format_field)
            if clean_format:
                name_field = form['name']
                name_field.field.widget.attrs['disabled'] = False
                name_field.field.widget.attrs['autofocus'] = True

                layers = [layer[0] for layer in name_field.field.choices]
                name_value = data.get('name', '')
                if name_value == '' or name_value not in layers:
                    name_value = util_helpers.get_first_substring_match(url_value, layers)
                if not name_value:
                    name_value = layers[0]
                form.data.update({'name': name_value})
                form.full_clean()

        message_template = 'library/share_dataset/message.html'
        message_tags = 'share-dataset-form message-template'

        dataset_handler = cache.get(form.cached_handler_key)
        url_instance = None

        form_is_valid = form.is_valid()
        clean_data = form.cleaned_data
        
        if form_is_valid and dataset_handler:
            url_instance, created = lib_models.URL.objects.get_or_create(
                url=dataset_handler.access_url,
            )
            if url_instance:
                dataset_queryset = lib_models.Dataset.objects.filter(
                    url=url_instance,
                    format=clean_data['format'],
                    name=clean_data['name'],
                )
                if dataset_queryset.exists():
                    dataset_instance = dataset_queryset.first()
                    messages.info(request, message_template, message_tags)

        if data.get('submit') is not None and not dataset_instance:
            if form_is_valid and url_instance:
                dataset_instance, created = lib_models.Dataset.objects.get_or_create(
                    url=url_instance,
                    format=clean_data['format'],
                    name=clean_data['name'],
                )
                if dataset_instance:
                    if created:
                        lib_models.Content.objects.create(
                            added_by=user,
                            dataset=dataset_instance,
                        )
                        dataset_handler.populate_dataset(dataset_instance)
                        messages.success(request, message_template, message_tags)
                    else:
                        messages.info(request, message_template, message_tags)
            else:
                messages.error(request, message_template, message_tags)

    return render(request, 'library/share_dataset/form.html', {
        'form':form, 
        'dataset':dataset_instance,
    })

@require_http_methods(['POST'])
def cors_proxy(request):
    url = request.GET.get('url')

    try:
        data = json.loads(request.body.decode('utf-8'))
        method = str(data.get('method', 'get'))
        
        if method.lower() == 'get':
           response = requests.get(url)
        elif method == 'post':
            response = requests.post(url, json=data)
        else:
            return JsonResponse({'error': f'Unsupported method: {method}'}, status=400)
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        return JsonResponse({'error': f'Error during request: {str(e)}'}, status=500)

    return JsonResponse(response.json())