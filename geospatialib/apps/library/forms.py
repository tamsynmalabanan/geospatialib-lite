from django import forms
from django.urls import reverse_lazy
from django.core.cache import cache

from . import models, choices
from ..utils.general import form_helpers, util_helpers
from ..utils.gis import dataset_helpers

class NewDatasetForm(forms.Form):
    path = forms.URLField(
        label='URL',
        required=True,
        widget=forms.URLInput(attrs={
            'hx-post':reverse_lazy('htmx:share_dataset'),
            'hx-trigger':'input changed delay:1000ms',
        })
    )
    format = forms.ChoiceField(
        label='Format', 
        choices=form_helpers.dict_to_choices(choices.DATASET_FORMATS, blank_choice=''), 
        required=True,
        error_messages={
            'required': 'Select a format.',
        },
        widget=forms.Select(attrs={
            'hx-post':reverse_lazy('htmx:share_dataset'),
            'hx-trigger':'change delay:1000ms',
            'disabled': True
        })
    )
    name = forms.ChoiceField(
        label='Layer', 
        required=True,
        error_messages={
            'required': 'Select a layer.',
        },
        widget=forms.Select(attrs={
            'hx-post':reverse_lazy('htmx:share_dataset'),
            'hx-trigger':'change delay:1000ms',
            'onchange':'disabledShareDatasetSubmitBtn()',
            'disabled':True,
        })
    )

    @property
    def cache_key(self):
        clean_data = self.cleaned_data
        path = clean_data.get('path')
        format = clean_data.get('format')
        if path and format:
            return util_helpers.build_cache_key(
                self.__class__.__name__, path, format)

    def clean_format(self):
        clean_data = self.cleaned_data
        format = clean_data.get('format')
        if not self.fields['name'].choices:
            path = clean_data.get('path')
            if path and format:
                cache_key = self.cache_key
                layers = cache.get(cache_key)
                if not layers:
                    layers = dataset_helpers.get_dataset_layers(path, format)
                if layers:
                    cache.set(cache_key, layers, timeout=3600)
                    self.fields['name'].choices = form_helpers.dict_to_choices(layers)
                else:
                    raise forms.ValidationError('No layers retrived in this format.')
        return format