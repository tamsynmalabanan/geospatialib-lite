from . import forms as main_forms
from django.contrib import messages

def forms(request):
    if not request.headers.get('HX-Request'):
        user = request.user
        if user.is_authenticated:
            if user.has_no_password:
                messages.info(request, 'Please set a login password for your account.', extra_tags='password-form')
            if user.has_no_first_name:
                messages.info(request, 'Please review or update details in your profile.', extra_tags='profile-form')
            return {
                'account_forms': main_forms.get_account_forms(user),
                'active_account_form': 'password' if user.has_no_password else 'profile'
            }
        else:
            messages.info(request, 'main/login/message.html', extra_tags='login-form message-template')
            return {
                'login_form': main_forms.AuthenticationForm()
            }
        
    return {}