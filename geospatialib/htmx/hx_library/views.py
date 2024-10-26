from django.views.decorators.http import require_http_methods
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.contrib import messages
from django.views.generic.list import ListView

from apps.library import (
    forms as lib_forms, 
    choices as lib_choices, 
    models as lib_models
)
from utils.general import form_helpers, util_helpers
from utils.gis import dataset_helpers


@require_http_methods(['GET'])
def search(request):
    print(request.GET)

    # websearch
    # SearchQuery(
    # ...     "'tomato' ('red' OR 'green')", search_type="websearch"
    # ... )
    # search params -- query and bounding box (optional)
    # Results for "query here" (count)
    # facet filters: resource (map/dataset), format
    # exclude facet filters with 0 count
    # filters are highlighted when active

    queryset = None

    if queryset is None:
        queryset = lib_models.Dataset.objects.prefetch_related('url').all()
    return render(request, 'library/search/results.html', {'datasets':queryset})


class SearchList(ListView):
    template_name = 'library/search/result_list.html'
    model = ''


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