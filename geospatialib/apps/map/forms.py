from django import forms
from django.urls import reverse_lazy
from django.core.cache import cache
from django.db.models import Q
from apps.library import models as lib_models
from . import models as map_models
from utils.general import form_helpers, util_helpers, model_helpers
from utils.gis import dataset_helpers
import json
import validators
from django.forms.models import model_to_dict, ModelMultipleChoiceField
from django.contrib.gis.geos import Polygon, GEOSGeometry



def get_map_edit_forms(name=None):
    forms = {
        'info': (3, EditMapInfoForm),
    }

    if name:
        return forms.get(name, None)

    return forms

class MapAbstractForm(forms.Form):

    def __init__(self, *args, map_instance=None, role=None, owner_pk=None, **kwargs):
        self.map_instance = map_instance
        self.content_instance = map_instance.content if map_instance else None
        self.map_dict = form_helpers.normalize_values_for_form(model_to_dict(map_instance)) if map_instance else None
        self.content_dict = form_helpers.normalize_values_for_form(model_to_dict(self.content_instance)) if self.content_instance else None
        self.role = role
        self.owner_pk = (
            owner_pk if owner_pk 
            else self.map_dict['owner'] if self.map_dict 
            else None
        )
        super().__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        initial = self.fields['title'].initial

        if self.role and self.role < 4 and title != initial:
            self.data.update({'title':initial})
            raise forms.ValidationError('Only the owner may assign the map title.')

        if len(title) < 3:
            raise forms.ValidationError('Title must be at least 3 characters.')
        
        if self.owner_pk:
            content_query = (
                lib_models.Content.objects
                .select_related('map', 'map__owner')
                .filter(
                    map__owner__pk=self.owner_pk,
                    title__iexact=title
                )
            )
    
            if self.map_dict:
                content_query = content_query.exclude(map__pk=self.map_dict['id'])
    
            if content_query.exists():
                content_instance = content_query.first()
                url = reverse_lazy('map:index', kwargs={'pk':content_instance.pk})
                raise forms.ValidationError(f'You already have a map with a similar title <a tabindex="-1" target="_blank" class="text-reset" href="{url}">here.</a>')

        return title

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
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

class MapReferenceForm(forms.ModelForm):
    label = forms.CharField(
        label='Label',
        max_length=255, 
        required=False
    )
    url_string = forms.URLField(
        label='URL',
        required=False,
    )

    class Meta:
        model = map_models.MapReference
        exclude = ['map', 'order', 'url']

    def valid_reference(self):
        valid_form = self.is_valid()
        return (
            valid_form
            and validators.url(self.cleaned_data.get('url_string'))
            and self.cleaned_data.get('label') not in ['', None]
        )

    def clean_url_string(self):
        url = self.cleaned_data.get('url_string')

        if url not in ['', None] and not validators.url(url):
            raise forms.ValidationError('URL is not valid.')
        
        return url
                   
    def clean_label(self):
        label = self.cleaned_data.get('label')
        if label not in ['', None] and len(label) < 3:
            raise forms.ValidationError('Label must be at least 3 characters.')
        return label

class BaseMapReferenceFormset(forms.BaseFormSet):
    deletion_widget = forms.HiddenInput()
    ordering_widget = forms.HiddenInput()
    
    def clean(self):
        if not any(self.errors):
            urls = []
            for form in self.forms:
                if self.can_delete and self._should_delete_form(form):
                    continue
            
                url = form.cleaned_data.get('url_string')
                label = form.cleaned_data.get('label')

                if any([url, label]) and not all([url, label]):
                    if label and not url:
                        form.add_error('url_string', 'This field is required.')
                    if not label and url:
                        form.add_error('label', 'This field is required.')

                if url and url in urls:
                    form.add_error('url_string', 'URL is already used in one of the entries above.')
                urls.append(url)

        if any(self.errors):
           raise forms.ValidationError('Please review below error/s:')
        
MapReferenceFormset = forms.formset_factory(
    MapReferenceForm, 
    formset=BaseMapReferenceFormset, 
    extra=1, 
    can_order=True,
    can_delete=True, 
    can_delete_extra=True
)

class EditMapInfoForm(MapAbstractForm):
    title = forms.CharField(
        label='Title', 
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'hx-post': None,
            'hx-trigger':'input changed delay:1000ms',
            'hx-target':'#mapDetails',
            'hx-swap': 'outerHTML',
        })
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
        help_text='On edit mode, adjusting the map also updates its default bounding box. Click the reset view icon <i class="bi bi-globe-americas"></i> before saving to undo changes in the bounding box.',
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
            'hx-post': None,
            'hx-trigger': 'tagsinput:change',
            'hx-target':'#mapDetails',
            'hx-swap': 'outerHTML',

            'data-role': 'tagsinput',
            'data-datalist-endpoint': reverse_lazy('hx_map:tags_datalist'),
        })
    )
    references = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'hx-post': None,
            'hx-trigger':'formset:change delay:2000ms',
            'hx-target':'#mapDetails',
            'hx-swap': 'outerHTML',
            'meta': {
                'formset':None,
            }
        })
    )

    def clean_references(self):
        references_formset = MapReferenceFormset(self.data, prefix='references')
        if 'references-TOTAL_FORMS' in self.data:
            self['references'].field.widget.attrs['meta']['formset'] = references_formset

        if not references_formset.is_valid():
            for form in references_formset:
                for field_name in form.errors.keys():
                    field = form[field_name]
                    form_helpers.validate_field(field)

            nonform_errors = references_formset.non_form_errors()
            if nonform_errors:
                raise forms.ValidationError(nonform_errors)
            else:
                raise forms.ValidationError('Please review below error/s:')

        all_changed = all(form.has_changed() for form in references_formset)
        return_form = 'submit' not in self.data or not self.is_valid()
        if all_changed and return_form:
            forms_count = len(references_formset.forms)
            extra_form = MapReferenceFormset(prefix='references').forms[-1]
            extra_form.prefix = f'references-{forms_count}'
            references_formset.forms.append(extra_form)
            references_formset.management_form.data.update({'references-TOTAL_FORMS': forms_count+1})

        references_data = []
        for form in references_formset:
            if form.valid_reference():
                order = form.cleaned_data.get('ORDER')
                data = {
                    'url_string': form.cleaned_data.get('url_string'),
                    'label': form.cleaned_data.get('label'),
                    'ORDER': order if order else 0,
                }
                if not references_formset.can_delete or not references_formset._should_delete_form(form):
                    references_data.append(data)
        
        self.data.update({'references':json.dumps(references_data)})
        return references_data
            
    def __init__(self, *args, user=None, section=None, **kwargs):
        self.section = section
        self.user = user
        super().__init__(*args, **kwargs)

        self.initial = self.content_dict
        self.initial.update(self.map_dict)
        
        if self.role and self.role < 4:
            title_field = self['title']
            title_field.field.initial = self.content_dict['title']
            title_field.field.widget.attrs['hidden'] = True

        for field_name in ['title', 'tags', 'references']:
            self[field_name].field.widget.attrs['hx-post'] = reverse_lazy(
                'hx_map:edit_map', 
                kwargs={
                    'pk':self.map_dict['id'],
                    'section':self.section,
                }
            )

        self.current_references = self.map_instance.references.all()
        initial_references = [
            {'url_string':i.url.url,'label':i.label,'ORDER':i.order} 
            for i in self.current_references
        ]
        self['references'].field.widget.attrs['meta']['formset'] = MapReferenceFormset(
            prefix='references', 
            initial=initial_references
        )
        self['references'].initial = json.dumps(initial_references)

    def save(self):
        updated_map = False
        updated_content = False
        for field, value in self.cleaned_data.items():
            if field in self.changed_data:
                if field == 'tags':
                    tag_instances = model_helpers.list_to_tags(value.split(','))
                    self.content_instance.tags.set(tag_instances)
                elif field == 'references':
                    for data in value:
                        url = data['url_string']
                        if validators.url(url):
                            url_instance, created = lib_models.URL.objects.get_or_create(url=url)
                            if url_instance:
                                reference_instance, created = map_models.MapReference.objects.get_or_create(
                                    map_id=self.map_dict['id'],
                                    url=url_instance,
                                )
                                if reference_instance:
                                    reference_instance.label = data['label']
                                    reference_instance.order = data['ORDER'] if data['ORDER'] else 0
                                    reference_instance.added_by = self.user
                                    reference_instance.updated_by = self.user
                                    reference_instance.save()
                    deleted_queryset = self.current_references.filter(~Q(url__url__in=[data['url_string'] for data in value]))
                    if deleted_queryset.exists():
                        deleted_queryset.delete()
                else:
                    if hasattr(self.map_instance, field):
                        setattr(self.map_instance, field, value)
                        updated_map = True
                    
                    if hasattr(self.content_instance, field):
                        setattr(self.content_instance, field, value)
                        updated_content = True

        if updated_map:
            self.map_instance.save()
            # self.map_instance.create_logs(self.map_dict)
        
        if updated_content:
            self.content_instance.save()
            # self.content_instance.create_logs(self.content_dict)