from django.contrib import messages

from apps.library import forms as lib_forms

def forms(request):
    if not request.headers.get('HX-Request'):
        user = request.user
        if user.is_authenticated:
            return {
                'share_dataset_form': lib_forms.ShareDatasetForm()
            }
        
    return {}