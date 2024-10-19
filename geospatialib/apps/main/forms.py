from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm

class AuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Email address or username')
