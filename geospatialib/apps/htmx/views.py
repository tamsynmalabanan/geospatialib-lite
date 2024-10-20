from django.shortcuts import render, HttpResponse
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout, login as login_user
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse


from urllib.parse import urlparse, parse_qs

from ..main import forms as main_forms
from ..library import forms as library_forms, choices as library_choices
from ..utils.general import form_helpers, util_helpers
from ..utils.gis import dataset_helpers

User = get_user_model()


def login(request):
    if request.method == 'POST':
        user = request.user
        form = main_forms.AuthenticationForm(request, request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
        
        if isinstance(user, User):
            login_user(request, user)

            referer = request.META.get('HTTP_REFERER')
            if referer:
                parsed_url = urlparse(referer)
                next_url = parse_qs(parsed_url.query).get('next')
                if next_url and next_url != '':
                    next_url = next_url[0]
                else:
                    next_url = referer
            else:
                next_url = reverse_lazy('library:index')
            response = HttpResponse()
            response['HX-Redirect'] = next_url
            return response
        else:
            messages.error(request, 'Invalid login credentials.', extra_tags='login-form')
    else:
        form = main_forms.AuthenticationForm()
        messages.info(request, 'main/login/message.html', extra_tags='login-form message-template')

    return render(request, 'main/login/form.html', {'form':form})

@login_required
def user_account(request, name):
    user = request.user
    forms = {
        'password': main_forms.SetPasswordForm(user=user),
    }

    if request.method == 'POST':
        form = forms[name]
        form.data = request.POST.dict()
        return render(request, f'main/account/{name}.html', {'form':form})
    
    return render(request, 'main/account/forms.html', {'forms':forms})

@login_required
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

            if data.get('submit', None) is not None:
                if form.is_valid():
                    print('save dataset')
                else:
                    print(form.errors)

    return render(request, 'library/new_dataset/form.html', {'form':form})