from django.shortcuts import render, HttpResponse
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login as login_user
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.password_validation import get_default_password_validators, validate_password as vp

from urllib.parse import urlparse, parse_qs

from ..main import forms as main_forms
from ..library import (
    forms as lib_forms, 
    choices as lib_choices, 
    models as lib_models
)
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
            if 'captcha' in form.errors:
                message = list(form.errors['captcha'].data[0])[0]
                if message == 'This field is required.':
                    message = 'You must pass the reCAPTCHA test to login. Please try again.'
            else:
                message = '<ul class="list-unstyled m-0">'
                for error in list(form.errors.values()):
                    clean_error = list(error.data[0])[0]
                    clean_error = clean_error.replace('Email', 'email or username')
                    message = message + '<li>' + clean_error + '</li>'
                message = message + '</ul>'
            messages.error(request, message, 'login-form')
    else:
        form = main_forms.AuthenticationForm()
        messages.info(request, 'main/login/message.html', extra_tags='login-form message-template')

    return render(request, 'main/login/form.html', {'form':form})


@login_required
def user_account(request, name):
    user = request.user
    forms = {
        'profile': main_forms.UserProfileForm(instance=user),
        'password': main_forms.SetPasswordForm(user=user),
    }

    if request.method == 'POST' and name in forms:
        form_class = forms[name].__class__
        if name == 'password':
            form = form_class(user=user, data=request.POST)
            if form.is_valid():
                if not user.check_password(form.cleaned_data.get('new_password1')):
                    user = form.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, f'You have successfully updated your password.', extra_tags=f'password-form')
                else:
                    messages.info(request, f'No changes made to your password.', extra_tags=f'password-form')
            else:
                message = '<ul class="list-unstyled m-0">'
                for error in list(form.errors.values()):
                    message = message + '<li>' + list(error.data[0])[0] + '</li>'
                message = message + '</ul>'
                messages.error(request, message, 'password-form')
            form = forms[name]
        else:
            form = form_class(instance=user, data=request.POST)
            if form.is_valid():
                if len(form.changed_data) != 0:
                    user = form.save()
                    messages.success(request, f'You have successfully updated your {name}.', extra_tags=f'{name}-form')
                else:
                    messages.info(request, f'No changes made to your {name}.', extra_tags=f'{name}-form')
            else:
                messages.error(request, 'Please review the error/s below.', f'{name}-form')
                for field in form.errors:
                    form_helpers.validate_field(form[field])
        return render(request, f'main/account/{name}.html', {'form':form})
    
    if user.has_no_password:
        messages.info(request, 'Please set a login password for your account.', extra_tags='password-form')
    if user.has_no_first_name:
        messages.info(request, 'Please review or update details in your profile.', extra_tags='profile-form')

    return render(request, 'main/account/forms.html', {
        'forms':forms,
        'active': 'password' if user.has_no_password else 'profile'
    })

@require_http_methods(['POST'])
@login_required
def password_validation(request):
    user = request.user
    data = {name:value for name, value in request.POST.items() if 'new_password' in name}
    form = main_forms.SetPasswordForm(user=user, data=data)
    form.validate_password(user)
    return render(request, 'main/account/password_validation.html', {'form':form})

@require_http_methods(['POST'])
@login_required
def username_validation(request):
    user = request.user
    form = main_forms.UserProfileForm(instance=user, data=request.POST.dict())
    username_field = form['username']
    if form.data['username'] == '':
        form.data.update({'username':user.username})
    if 'username' in form.changed_data:
        form_helpers.validate_field(username_field, style_if_valid=True)
    return render(request, 'base/components/form/field.html', {'field': username_field})

@require_http_methods(['GET'])
@login_required
def generate_random_username(request):
    user = request.user
    form = main_forms.UserProfileForm(instance=user, data=request.GET.dict())
    username_field = form['username']
    
    random_username = User.objects.generate_random_username(user=user)
    form.data.update({'username':random_username})
    form_helpers.validate_field(username_field, style_if_valid=True)
    
    return render(request, 'base/components/form/field.html', {'field': username_field})


@require_http_methods(['GET'])
def search(request):
    print(request.GET)
    
    queryset = None

    if queryset is None:
        queryset = lib_models.Dataset.objects.prefetch_related('url').all()
    return render(request, 'library/search/results.html', {'datasets':queryset})


@login_required
def share_dataset(request):
    user = request.user
    dataset_instance = None
    
    form = lib_forms.NewDatasetForm(data={})
    if request.method == 'POST':
        data = request.POST.dict()
        path_value = data.get('path', '')
        if path_value.strip() != '':
            path_field = form['path']
            form.data.update({'path':path_value})
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
                    name_field.field.widget.attrs['autofocus'] = True

                    layers = [layer[0] for layer in name_field.field.choices]
                    name_value = data.get('name', '')
                    if name_value == '' or name_value not in layers:
                        name_value = util_helpers.get_first_substring_match(path_value, layers)
                    if not name_value:
                        name_value = layers[0]
                    form.data.update({'name': name_value})
                    form.full_clean()

            message_template = 'library/share_dataset/message.html'
            message_tags = 'share-dataset-form message-template'

            dataset_handler = cache.get(form.cached_handler_key)
            url_instance = None

            form_is_valid = form.is_valid()
            clean_data = form.cleaned_data
            
            if form_is_valid and dataset_handler:
                url_instance, created = lib_models.URL.objects.get_or_create(
                    path=dataset_handler.access_url,
                    defaults={'added_by':user}
                )
                if url_instance:
                    dataset_queryset = lib_models.Dataset.objects.filter(
                        url=url_instance,
                        format=clean_data['format'],
                        name=clean_data['name'],
                    )
                    if dataset_queryset.exists():
                        dataset_instance = dataset_queryset.first()
                        messages.info(request, message_template, message_tags)

            if data.get('submit') is not None and not dataset_instance:
                if form_is_valid and url_instance:
                    dataset_instance, created = lib_models.Dataset.objects.get_or_create(
                        url=url_instance,
                        format=clean_data['format'],
                        name=clean_data['name'],
                        defaults={'added_by':user}
                    )
                    if dataset_instance:
                        if created:
                            dataset_handler.populate_dataset(dataset_instance)
                            messages.success(request, message_template, message_tags)
                        else:
                            messages.info(request, message_template, message_tags)
                else:
                    messages.info(request, message_template, message_tags)

    return render(request, 'library/share_dataset/form.html', {'form':form, 'dataset':dataset_instance})