from django import template

from ..general import form_helpers

register = template.Library()

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

