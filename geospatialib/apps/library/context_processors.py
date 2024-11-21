from django.contrib import messages

from apps.library import forms as lib_forms
from htmx.hx_library import views

def forms(request):
    if not request.headers.get('HX-Request'):
        user = request.user
        if user.is_authenticated:
            return {
                'share_dataset_form': lib_forms.ShareDatasetForm(),
                'create_map_form': lib_forms.CreateMapForm(),
            }
    
    return {}