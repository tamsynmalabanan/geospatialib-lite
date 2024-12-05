from django.contrib import messages

from . import forms as map_forms, models as map_models
from htmx.hx_library import views

def forms(request):
    if not request.headers.get('HX-Request'):
        user = request.user
        if user.is_authenticated:
            return {
                'create_map_form': map_forms.CreateMapForm()
            }
    
    return {}