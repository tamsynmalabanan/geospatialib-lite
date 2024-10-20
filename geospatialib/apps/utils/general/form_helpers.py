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

def validate_field(field):
    valid = field.name not in field.form.errors
    if valid:
        remove_classes_from_field(field, ['is-invalid'])
    else:
        append_classes_to_field(field, ['is-invalid'])
    return valid

def assign_field_style_classes(field):
    field_classes = []
    
    input_type = field.field.widget.input_type
    if input_type == 'select':
        field_classes.append('form-select')
    elif input_type == 'checkbox':
        field_classes.append('form-check-input') 
    else:
        field_classes.append('form-control')
    
    append_classes_to_field(field, field_classes)

def assign_field_attributes(field):
    attrs = field.field.widget.attrs
    attrs['id'] = f'{field.form.__class__.__name__.lower()}_{field.name}'
    attrs['placeholder'] = field.label

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