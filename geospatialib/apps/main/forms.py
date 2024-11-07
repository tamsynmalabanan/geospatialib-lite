from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.password_validation import get_default_password_validators, validate_password as vp
from django.contrib.auth import get_user_model, authenticate
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


User = get_user_model()

def get_account_forms(user, data=None, name=None):
    if data:
        forms= {
            'profile': UserProfileForm(instance=user, data=data),
            'password': SetPasswordForm(user=user, data=data),
        }
    else:
        forms = {
            'profile': UserProfileForm(instance=user),
            'password': SetPasswordForm(user=user),
        }

    if name and name in forms:
        return forms[name]
    
    return forms
    


class AuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Email address or username')
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

class SetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New password', 
        max_length=32, 
        required=True,
        widget=forms.PasswordInput(attrs={
            'hx-post': reverse_lazy('hx_main:password_validation'),
            'hx-trigger': 'input changed delay:500ms',
            'hx-target':'#accountPasswordFormValidationFields',
            'hx-swap':'outerHTML',
        })
    )
    new_password2 = forms.CharField(
        label='New password confirmation', 
        max_length=32, 
        required=True,
        widget=forms.PasswordInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        password_validation_fields = {
            validator.__class__.__name__:validator.get_help_text() 
            for validator in get_default_password_validators()
        }
        
        for field_name, label in password_validation_fields.items():
            self.fields[field_name] = forms.BooleanField(
                label=label,
                initial=False,
                required=True,
                widget=forms.CheckboxInput(attrs={
                    'class':'box-shadow-none',
                    'onclick':'return false;',
                    'tabindex':'-1', 
                }),
            )

    def validate_password(self, user):
        new_password1 = self.data.get('new_password1','')
        if new_password1 != '':
            for validator in get_default_password_validators():
                validator_name = validator.__class__.__name__
                attrs = self.fields[validator_name].widget.attrs
                try:
                    vp(new_password1, user, [validator])
                    attrs['checked'] = True
                except Exception as e:
                    if 'checked' in attrs:
                        del attrs['checked']

class UserProfileForm(forms.ModelForm):
    username = forms.CharField(
        label='Username', 
        max_length=32, 
        required=True,
        widget=forms.TextInput(attrs={
            'hx-post': reverse_lazy('hx_main:username_validation'),
            'hx-trigger': 'input changed delay:500ms',
            'hx-target':'.field-container:has(input[name="username"])',
            'hx-swap':'outerHTML',
        })
    )
    first_name = forms.CharField(
        label='First name',
        max_length=32, 
        required=True,
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']