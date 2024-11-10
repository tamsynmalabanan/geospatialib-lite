from django.shortcuts import render, HttpResponse
from django.core.paginator import Paginator

from . import forms, models
from htmx.hx_library.views import SearchList

def index(request):
    form = forms.SearchForm(data=request.GET)
    context = {'form':form}
    if form.is_valid():
        search_list = SearchList(request=request)
        queryset = search_list.get_queryset()
        context['filters'] = search_list.get_filters()

        paginator = Paginator(queryset, search_list.paginate_by)
        context['page_obj'] = paginator.get_page(1)

    return render(request, 'library/index.html', context)