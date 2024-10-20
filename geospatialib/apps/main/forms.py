from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.password_validation import get_default_password_validators, validate_password as vp


class AuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Email address or username')

class SetPasswordForm(SetPasswordForm):
    # new_password1 = forms.CharField(
    #     label='New password',
    #     widget=forms.PasswordInput(attrs={
    #         "hx-post": reverse_lazy('htmx:validate_password'),
    #         "hx-trigger": 'keyup changed delay:1000ms',
    #         "hx-sync": "closest form:abort",
    #         'extra_attrs': {
    #             'control_button': {
    #                 'icon': 'bi bi-incognito',
    #                 'attrs': {
    #                     'title': 'Click to generate a random password',
    #                     'hx-get': reverse_lazy('htmx:generate_random_password'),
    #                     'hx-swap': 'outerHTML',
    #                     'hx-trigger':"click delay:1000ms",
    #                 }
    #             }
    #         }
    #     },),
    # )
    # new_password2 = forms.CharField(
    #     label='New password confirmation',
    #     widget=forms.PasswordInput(attrs={
    #         "hx-post": reverse_lazy('htmx:validate_password'),
    #         "hx-trigger": 'keyup changed delay:1000ms',
    #         "hx-sync": "closest form:abort",
    #     },),
    # )

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

        self.order_fields(['new_password1'] + list(password_validation_fields.keys()) + ['new_password2'])

