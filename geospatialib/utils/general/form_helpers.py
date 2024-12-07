from django_recaptcha.widgets import ReCaptchaV2Checkbox

from collections import OrderedDict
import random
import string

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
    attrs['id'] = f'{field.form.__class__.__name__.lower()}_{field.name}'

    print(field)

    if isinstance(widget, ReCaptchaV2Checkbox):
        pass
        # attrs['data-theme'] = 'light'
        # attrs['data-size'] = 'normal'
    else:
        attrs['placeholder'] = field.label

    if attrs.get('data-role') == 'tagsinput':
        attrs['hidden'] = True

    if 'data-datalist-endpoint' in attrs:
        attrs['list'] = f'{field.id_for_label}_datalist'

def black_choices(value='---------'):
    return [('', value)]

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