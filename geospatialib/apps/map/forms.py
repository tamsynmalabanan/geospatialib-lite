from django import forms
from django.urls import reverse_lazy
from django.core.cache import cache

from apps.library import models as lib_models
from utils.general import form_helpers, util_helpers
from utils.gis import dataset_helpers

class CreateMapForm(forms.Form):
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

    def clean_title(self):
        clean_data = self.cleaned_data
        title = clean_data.get('title')

        if len(title) < 3:
            raise forms.ValidationError('Title must be at least 3 characters.')

        try:
            content_instance = lib_models.Content.objects.get(
                map__owner__pk=self.data.get('owner'),
                label__iexact=title
            )
        except:
            content_instance = None

        if content_instance:
            url = reverse_lazy('map:index', kwargs={'pk':content_instance.pk})
            raise forms.ValidationError(f'You already have a map with a similar title <a target="_blank" class="text-reset" href="{url}">here.</a>')

        return title

    def clean_tags(self):
        clean_data = self.cleaned_data
        tags = clean_data.get('tags')
        clean_tags = ','.join(util_helpers.split_by_special_characters(tags, ['_', '-', ','])).lower()
        return clean_tags