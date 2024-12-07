from django import forms
from django.urls import reverse_lazy
from django.core.cache import cache

from apps.library import models as lib_models
from . import models as map_models
from utils.general import form_helpers, util_helpers
from utils.gis import dataset_helpers
import json

def get_map_edit_forms(name=None):
    forms = {
        'info': (3, EditMapInfoForm),
    }

    if name:
        return forms.get(name, None)

    return forms

class MapAbstractForm(forms.Form):

    def clean_title(self):
        clean_data = self.cleaned_data
        title = clean_data.get('title')
        owner_pk = self.data.get('owner')
        map_pk = self.data.get('map')
        role = self.data.get('role')
        initial = self.fields['title'].initial

        if role and role < 4 and title != initial:
            self.data.update({'title':initial})
            raise forms.ValidationError('Only the owner may assign the map title.')

        if len(title) < 3:
            raise forms.ValidationError('Title must be at least 3 characters.')

        content_query = lib_models.Content.objects.filter(
            map__owner__pk=owner_pk,
            title__iexact=title
        )

        if map_pk:
            content_query = content_query.exclude(map__pk=map_pk)

        if content_query.exists():
            url = reverse_lazy('map:index', kwargs={'pk':content_query.first().pk})
            raise forms.ValidationError(f'You already have a map with a similar title <a target="_blank" class="text-reset" href="{url}">here.</a>')

        return title

    def clean_tags(self):
        clean_data = self.cleaned_data
        tags = clean_data.get('tags')
        clean_tags = ','.join(util_helpers.split_by_special_characters(tags, ['_', '-', ','])).lower()
        self.data.update({'tags':clean_tags})
        return clean_tags

class CreateMapForm(MapAbstractForm):
    title = forms.CharField(
        label='Title', 
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'hx-post':reverse_lazy('hx_map:create_map'),
            'hx-trigger':'input changed delay:1000ms',
            'hx-target':'#createMapFormFields',
            'hx-swap': 'innerHTML',
        })
    )
    tags = forms.CharField(
        label='Add a tag',
        required=True,
        error_messages={
            'required': 'Add at least one tag.',
        },
        widget=forms.TextInput(attrs={
            'hx-post':reverse_lazy('hx_map:create_map'),
            'hx-trigger': 'tagsinput:change',
            'hx-target':'#createMapFormFields',
            'hx-swap': 'innerHTML',

            'data-role': 'tagsinput',
            'data-datalist-endpoint': reverse_lazy('hx_map:tags_datalist'),
        })
    )
    focus_area = forms.CharField(
        label='Focus area', 
        max_length=255,
        required=False,
    )
    bbox = forms.CharField(widget=forms.Textarea(attrs={'hidden':True}))

class EditMapInfoForm(MapAbstractForm):
    title = forms.CharField(
        label='Title', 
        max_length=255,
        required=True,
    )
    focus_area = forms.CharField(
        label='Focus area', 
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class':'geospatialibMap-geocoder-field'
        })
    )
    bbox = forms.CharField(
        label='Bounding box',
        widget=forms.Textarea(attrs={
            'hidden':True,
            'class': 'geospatialibMap-bbox-field',
        })
    )
    abstract = forms.CharField(
        label='Abstract',
        required=False,
        widget=forms.Textarea(attrs={
            'style':'min-height: 200px;',
        })
    )
    tags = forms.CharField(
        label='Add a tag',
        required=True,
        error_messages={
            'required': 'Add at least one tag.',
        },
        widget=forms.TextInput(attrs={
            'data-role': 'tagsinput',
            'data-datalist-endpoint': reverse_lazy('hx_map:tags_datalist'),
        })
    )