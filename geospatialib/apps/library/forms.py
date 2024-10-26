from django import forms
from django.urls import reverse_lazy
from django.core.cache import cache

from . import models, choices
from utils.general import form_helpers, util_helpers
from utils.gis import dataset_helpers

class SearchForm(forms.Form):
    query = forms.CharField(
        label='Search...', 
        max_length=256, 
        required=True,
        widget=forms.TextInput(attrs={
            'type':'search',
            'class':'h-100 border-0 rounded-0 focus-underline-success box-shadow-none'
        })
    )

class NewDatasetForm(forms.Form):
    path = forms.URLField(
        label='URL',
        required=True,
        widget=forms.URLInput(attrs={
            'type':'search',
            'hx-post':reverse_lazy('hx_library:share_dataset'),
            'hx-trigger':'input changed delay:500ms',
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
            'hx-post':reverse_lazy('hx_library:share_dataset'),
            'hx-trigger':'change',
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
            'hx-post':reverse_lazy('hx_library:share_dataset'),
            'hx-trigger':'change',
            'onchange':'resetShareDatasetSubmitBtn()',
            'disabled':True,
        })
    )

    @property
    def cached_handler_key(self):
        clean_data = self.cleaned_data
        path = clean_data.get('path')
        format = clean_data.get('format')
        if path and format:
            return util_helpers.build_cache_key(
                'dataset-handler', 
                format, 
                path
            )
        
    def clean_format(self):
        clean_data = self.cleaned_data
        format = clean_data.get('format')

        if not self.fields['name'].choices:
            path = clean_data.get('path')
            if path and format:
                key = self.cached_handler_key
                handler = cache.get(key)
                if not handler or not handler.layers:
                    handler = dataset_helpers.get_dataset_handler(
                        format, 
                        path=path,
                        key=key,
                    ) 
                if handler and handler.layers:
                    self.fields['name'].choices = form_helpers.dict_to_choices(handler.layers)
                else:
                    raise forms.ValidationError('No layers retrived in this format.')
        
        return format