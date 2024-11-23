from django import forms
from django.urls import reverse_lazy
from django.core.cache import cache

from . import models, choices
from utils.general import form_helpers, util_helpers
from utils.gis import dataset_helpers

class SearchForm(forms.Form):
    query = forms.CharField(
        label='Search...', 
        max_length=255, 
        required=True,
        widget=forms.TextInput(attrs={
            'type':'search',
            'class':'h-100 border-0 rounded-0 focus-underline-primary box-shadow-none ps-0',
        })
    )

class CreateMapForm(forms.Form):
    title = forms.CharField(
        label='Title', 
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'hx-post':reverse_lazy('hx_library:create_map'),
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
            'hx-post':reverse_lazy('hx_library:create_map'),
            'hx-trigger': 'tagsinput:change',
            'hx-target':'#createMapFormFields',
            'hx-swap': 'innerHTML',

            'data-role': 'tagsinput',
            'data-datalist-endpoint': reverse_lazy('hx_library:tags_datalist'),
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

        content_query = models.Content.objects.filter(
            map__owner__pk=self.data.get('owner'),
            label__iexact=title
        )
        if content_query.exists():
            content_instance = content_query.first()
            url = reverse_lazy('library:map', kwargs={'pk':content_instance.pk})
            raise forms.ValidationError(f'You already have a map with a similar title <a target="_blank" class="text-reset" href="{url}">here.</a>')
        
        return title

    def clean_tags(self):
        clean_data = self.cleaned_data
        tags = clean_data.get('tags')
        clean_tags = ','.join(util_helpers.split_by_special_characters(tags, ['_', '-', ','])).lower()
        return clean_tags

class ShareDatasetForm(forms.Form):
    url = forms.URLField(
        label='URL',
        required=True,
        widget=forms.URLInput(attrs={
            'type':'search',
            'hx-post':reverse_lazy('hx_library:share_dataset'),
            'hx-trigger':'input changed delay:1000ms',
            'hx-target':'#shareDatasetFormFields',
            'hx-swap': 'innerHTML',
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
            'hx-target':'#shareDatasetFormFields',
            'hx-swap': 'innerHTML',
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
            'hx-target':'#shareDatasetFormFields',
            'hx-swap': 'innerHTML',
            'onchange':'resetShareDatasetSubmitBtn()',
            'disabled':True,
        })
    )

    @property
    def cached_handler_key(self):
        clean_data = self.cleaned_data
        url = clean_data.get('url')
        format = clean_data.get('format')
        if url and format:
            return util_helpers.build_cache_key(
                'dataset-handler', 
                format, 
                url
            )
        
    def clean_format(self):
        clean_data = self.cleaned_data
        format = clean_data.get('format')

        if not self.fields['name'].choices:
            url = clean_data.get('url')
            if url and format:
                key = self.cached_handler_key
                handler = cache.get(key)
                if not handler or not handler.layers:
                    handler = dataset_helpers.get_dataset_handler(
                        format, 
                        url=url,
                        key=key,
                    ) 
                if handler and handler.layers:
                    self.fields['name'].choices = form_helpers.dict_to_choices(handler.layers)
                else:
                    raise forms.ValidationError('No layers retrived in this format.')
        
        return format