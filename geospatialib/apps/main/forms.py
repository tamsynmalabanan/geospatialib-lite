from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.password_validation import get_default_password_validators, validate_password as vp
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


class AuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Email address or username')

class SetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New password', 
        max_length=32, 
        required=True,
        widget=forms.PasswordInput(attrs={
            'hx-post': reverse_lazy('htmx:password_validation'),
            'hx-trigger': 'input changed delay:1000ms',
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
                    'class':'focus-ring-none',
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
    first_name = forms.CharField(
        label='First name',
        max_length=32, 
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']