from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.db import models
from django.forms.models import ModelMultipleChoiceField
from collections import OrderedDict
import random
import string
from django import forms
from django.contrib.gis.geos import Polygon, GEOSGeometry

def generate_random_slug(length=16):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def append_classes_to_field(field, new_classes:list):
    attrs = field.field.widget.attrs
    current_classes = attrs.get('class', '').split(' ')
    attrs['class'] = ' '.join(list(set(current_classes + new_classes))).strip()

def remove_classes_from_field(field, excluded_classes:list):
    attrs = field.field.widget.attrs
    current_class = attrs.get('class', '').split(' ')
    attrs['class'] = ' '.join([i for i in current_class if i not in excluded_classes]).strip()

def validate_field(field, style_if_valid=False):
    valid = field.name not in field.form.errors
    if valid:
        remove_classes_from_field(field, ['is-invalid'])
        if style_if_valid:
            append_classes_to_field(field, ['is-valid'])
    else:
        append_classes_to_field(field, ['is-invalid'])
        if style_if_valid:
            remove_classes_from_field(field, ['is-valid'])
    return field.form.cleaned_data.get(field.name)

def assign_field_style_classes(field):
    field_classes = []
    
    widget = field.field.widget
    if isinstance(widget, ReCaptchaV2Checkbox):
        field_classes.append('d-flex')
        field_classes.append('justify-content-center')
    elif isinstance(widget, forms.CheckboxSelectMultiple):
        pass
    else:
        if hasattr(widget, 'input_type'):
            input_type = widget.input_type
        else:
            input_type = None

        if input_type == 'select':
            field_classes.append('form-select')
        elif input_type == 'checkbox':
            field_classes.append('form-check-input') 
        else:
            field_classes.append('form-control')

    append_classes_to_field(field, field_classes)

def assign_field_attributes(field):
    widget = field.field.widget
    
    attrs = widget.attrs

    id = f'{field.form.__class__.__name__.lower()}_{field.name}'
    attrs['id'] = id

    if not isinstance(widget, ReCaptchaV2Checkbox):
        attrs['placeholder'] = field.label

    if attrs.get('data-role') == 'tagsinput':
        attrs['hidden'] = True

    if 'data-datalist-endpoint' in attrs:
        attrs['list'] = f'{field.id_for_label}_datalist'

    meta_attrs = attrs.get('meta', {})
    if 'formset' in meta_attrs:
        formset = meta_attrs['formset']
        for form in formset:
            for name, formset_field in form.fields.items():
                append_classes_to_field(form[name], ['formset-field'])
                formset_field.widget.attrs['data-formset-field'] = f'#{id}'

def normalize_values_for_form(model_dict):
    for key, value in model_dict.items():
        if value and not isinstance(value, (str, int, float)):
            if isinstance(value, GEOSGeometry):
                model_dict[key] = value.geojson.replace(' ','')
            elif isinstance(value, list):
                model_dict[key] = ','.join([str(i) for i in value])
            else:
                print(key, value, type(value))
    return model_dict

def dict_to_choices(dict, blank_choice=None, sort=False):
    dict_copy = {'':str(blank_choice)} if blank_choice is not None else {}

    for key, value in dict.items():
        try:
            dict_copy[key] = str(value)
        except Exception as e:
            print('ERROR with dict_to_choices: ', e)

    if sort:
        dict_copy = OrderedDict(sorted(dict_copy.items(), key=lambda item: item[1]))
    
    return [(key, value) for key, value in dict_copy.items()]