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

def social(request):
    user = request.user
    if user.is_authenticated and user.socialaccount_set.exists():
        social_accounts = user.socialaccount_set.all()
        for i in social_accounts:
            profile_picture = i.extra_data.get('picture')
            if profile_picture:
                break
        print(profile_picture)
        return {
            'social_accounts': social_accounts,
            'profile_picture': profile_picture,
        }