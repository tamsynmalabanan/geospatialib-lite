from django.shortcuts import render, HttpResponse
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

from apps.main import forms as main_forms
from utils.general import form_helpers, util_helpers

User = get_user_model()

@require_http_methods(['POST'])
def login(request):
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
    return render(request, 'main/login/form.html', {'form':form})


@require_http_methods(['POST'])
@login_required
def user_account(request, name):
    user = request.user

    form = main_forms.get_account_forms(user, data=request.POST, name=name)

    if name == 'password':
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
        form = main_forms.get_account_forms(user, name=name)
    else:
        if form.is_valid():
            proper_name = name
            if name == 'privacy':
                proper_name = 'privacy settings'

            if len(form.changed_data) != 0:
                user = form.save()
                messages.success(request, f'You have successfully updated your {proper_name}.', extra_tags=f'{name}-form')
            else:
                messages.info(request, f'No changes made to your {proper_name}.', extra_tags=f'{name}-form')
        else:
            messages.error(request, 'Please review the error/s below.', f'{name}-form')
            for field in form.errors:
                form_helpers.validate_field(form[field])
    
    return render(request, f'main/account/{name}.html', {'form':form})

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