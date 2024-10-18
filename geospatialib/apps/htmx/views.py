from django.shortcuts import render
from django.core.cache import cache
import django_htmx


from ..library import forms as library_forms, choices as library_choices
from ..utils.general import form_helpers, util_helpers
from ..utils.gis import dataset_helpers

def new_dataset(request):
    form = library_forms.NewDatasetForm(data={})
    if request.method == 'POST':
        data = request.POST.dict()
        path_value = data.get('path', '')
        if path_value.strip() != '':
            form.data.update({'path':path_value})

            path_field = form['path']
            path_is_valid = form_helpers.validate_field(path_field)
            if path_is_valid:
                format_field = form['format']
                format_field.field.widget.attrs['disabled'] = False

                format_value = data.get('format', '')
                if format_value == '':
                    format_value = dataset_helpers.get_dataset_format(path_value)
                if format_value:
                    form.data.update({'format': format_value})
                    form.full_clean()
                    
                format_is_valid = form_helpers.validate_field(format_field)
                if format_is_valid:
                    name_field = form['name']
                    name_field.field.widget.attrs['disabled'] = False

                    layers = [layer[0] for layer in name_field.field.choices]
                    name_value = data.get('name', '')
                    if name_value == '' or name_value not in layers:
                        name_value = util_helpers.get_first_substring_match(path_value, layers)
                    if not name_value:
                        name_value = layers[0]
                    form.data.update({'name': name_value})
                    form.full_clean()

            if data.get('submit', '') == 'true':
                if form.is_valid():
                    print('save dataset')
                else:
                    print(form.errors)

    return render(request, 'library/new_dataset/form.html', {'form':form})