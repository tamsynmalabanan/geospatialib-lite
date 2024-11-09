from django.contrib import messages

from apps.library import forms as lib_forms
from htmx.hx_library import views

def forms(request):
    if not request.headers.get('HX-Request'):
        user = request.user
        if user.is_authenticated:
            return {
                'share_dataset_form': lib_forms.ShareDatasetForm()
            }
    
    return {}

def search(request):
    if not request.headers.get('HX-Request'):
        content_list = views.SearchList(request=request)
        contents = content_list.get_queryset()
        
        paginator = Paginator(contents, content_list.paginate_by)
        page_obj = paginator.get_page(1)
        
        return render(request, 'library/index/index.html', {
            'search_form': lib_forms.SearchForm(data=request.GET),
            'page_obj': page_obj,
        })
