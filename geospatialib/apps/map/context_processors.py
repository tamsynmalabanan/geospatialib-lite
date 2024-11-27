from django.contrib import messages

from .forms import CreateMapForm
from htmx.hx_library import views

def forms(request):
    if not request.headers.get('HX-Request'):
        user = request.user
        if user.is_authenticated:
            return {
                'create_map_form': CreateMapForm()
            }
    
    return {}