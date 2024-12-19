from django import template
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django import template
from django.utils import timezone

from ..general import form_helpers, model_helpers

import json
import shortuuid
from shapely.geometry import shape
from urllib.parse import urlparse
import random, string


register = template.Library()

@register.filter
def object_type(value):
    return str(type(value))

@register.filter
def vars_dict(value):
    return vars(value)

@register.filter
def append_timezone(value):
    if value:
        return f"{value} {timezone.get_current_timezone_name()}"
    return value

@register.filter
def get_field_verbose_name(instance, field_exp):
    field = model_helpers.get_field_from_instance(instance, field_exp)
    return field.verbose_name

@register.simple_tag
def random_string():
    chars = string.ascii_letters
    return ''.join(random.choices(chars, k=16))

@register.simple_tag
def var(value):
    return value

@register.simple_tag
def get_form_class_name(form):
    return form.__class__.__name__.lower()

@register.simple_tag
def assign_field_attributes(field):
    form_helpers.assign_field_attributes(field)
    form_helpers.assign_field_style_classes(field)
    
    return field

@register.filter
def is_captchta_widget(widget):
    return isinstance(widget, ReCaptchaV2Checkbox)

@register.filter
def field_name(exp):
    return exp.split('__')[-1]

@register.filter
def sub_bool(value, sub):
    if isinstance(value, bool):
        if value:
            return sub
        return f'not {sub}'
    return value

@register.filter
def get(dictionary, key):
    try:
        return dictionary.get(key)
    except:
        pass    
        

@register.filter
def stringify(value):
    return str(value)

@register.filter
def domain(url):
    return urlparse(url).netloc

@register.filter
def json_loads(string):
    try:
        return json.loads(string)
    except:
        return

@register.filter
def json_dumps(string):
    try:
        return json.dumps(string)
    except:
        return