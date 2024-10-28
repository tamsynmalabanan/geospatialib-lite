from django.db.models.query import QuerySet
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.contrib import messages
from django.views.generic.list import ListView
from django.db.models import Count, Sum, F, IntegerField, Value, Q, Case, When, Max, TextField, CharField, FloatField
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, SearchHeadline

import time

from apps.library import (
    forms as lib_forms, 
    choices as lib_choices, 
    models as lib_models
)
from utils.general import form_helpers, util_helpers
from utils.gis import dataset_helpers

class SearchList(ListView):
    template_name = 'library/search/results.html'
    model = lib_models.Content
    context_object_name = 'contents'
    paginate_by = 10

    def get_queryset(self):
        if not hasattr(self, 'queryset') or not getattr(self, 'queryset'):
            queryset = super().get_queryset()        

            queryset = queryset.filter(**{
                param:value 
                for param,value in self.request.GET.items() 
                if param not in ['query', 'page', 'bbox']
                and value not in ['', None]
            })

            query = self.request.GET.get('query')
            if query and query != '':
                search_query = SearchQuery(query, search_type="websearch")

                search_vector = (
                    SearchVector('type') + 
                    SearchVector('dataset__uuid') + 
                    SearchVector('dataset__url__tags__tag') + 
                    SearchVector('dataset__format') + 
                    SearchVector('dataset__name') + 
                    SearchVector('dataset__title') + 
                    SearchVector('dataset__data') + 
                    SearchVector('map__uuid') + 
                    SearchVector('map__title')
                )

                queryset = (
                    queryset
                    .prefetch_related('dataset', 'map')
                    .annotate(rank=SearchRank(search_vector, search_query))
                    .annotate(rank=Max('rank'))
                    .filter(rank__gte=0.001)
                    .order_by('-rank')
                )

            print(queryset.count())
            self.queryset = queryset
        return self.queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['filters'] = {
        #     field: (
        #         self.queryset
        #         .values(field)
        #         .annotate(count=Count('id'))
        #         .annotate(label=F(field))
        #         .order_by('-count')
        #     )
        #     for field in ['type', 'dataset__format']
        # }
        return context

@login_required
def share_dataset(request):
    user = request.user
    dataset_instance = None
    
    form = lib_forms.NewDatasetForm(data={})
    if request.method == 'POST':
        data = request.POST.dict()
        path_value = data.get('path', '')
        if path_value.strip() != '':
            path_field = form['path']
            form.data.update({'path':path_value})
            path_is_valid = form_helpers.validate_field(path_field)
            if path_is_valid:
                format_field = form['format']
                format_field.field.widget.attrs['disabled'] = False

                format_value = data.get('format', '')
                if format_value == '':
                    format_value = dataset_helpers.get_dataset_format(path_value)
                if format_value:
                    form.data.update({'format': format_value})
                    form.full_clean()
                
                format_is_valid = form_helpers.validate_field(format_field)
                if format_is_valid:
                    name_field = form['name']
                    name_field.field.widget.attrs['disabled'] = False
                    name_field.field.widget.attrs['autofocus'] = True

                    layers = [layer[0] for layer in name_field.field.choices]
                    name_value = data.get('name', '')
                    if name_value == '' or name_value not in layers:
                        name_value = util_helpers.get_first_substring_match(path_value, layers)
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
                    path=dataset_handler.access_url,
                    defaults={'added_by':user}
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
                        defaults={'added_by':user}
                    )
                    if dataset_instance:
                        if created:
                            dataset_handler.populate_dataset(dataset_instance)
                            lib_models.Content.objects.create(dataset=dataset_instance)
                            messages.success(request, message_template, message_tags)
                        else:
                            messages.info(request, message_template, message_tags)
                else:
                    messages.info(request, message_template, message_tags)

    return render(request, 'library/share_dataset/form.html', {'form':form, 'dataset':dataset_instance})