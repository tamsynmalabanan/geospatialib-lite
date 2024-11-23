from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages

from . import forms, models
from htmx.hx_library.views import SearchList

import json

def index(request):
    form = forms.SearchForm(data=request.GET)
    return render(request, 'library/index.html', {'form':form})

def map(request, pk):
    current_user = request.user

    try:
        map_instance = (
            models.Map.objects
            .select_related('content', 'owner')
            .prefetch_related('content__tags', 'roles', 'references')
            .values(*[
                'content__pk', 
                'content__label', 
                # 'content__bbox',
                # 'content__abstract',
                # 'content__tags__tag',

                # 'published',
                # 'privacy', 
                # 'focus_area',
                # 'references__url',
            ])
            .filter(content__pk=pk)
            .first()
        )
    except Exception as e:
        print(e)
        map_instance = None

    if map_instance:
        return render(request, 'library/map.html', {'map':map_instance})

    messages.error(request, 'Page not found. You have been redirected to the library.', 'map-floating-message')
    return redirect('library:index')