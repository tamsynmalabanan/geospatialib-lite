from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages

from utils.general import model_helpers
from . import forms, models
from htmx.hx_library.views import SearchList

import json

def index(request):
    form = forms.SearchForm(data=request.GET)
    return render(request, 'library/index.html', {'form':form})

def map(request, pk):
    user = request.user

    try:
        map_instance = (
            models.Map.objects
            .select_related('content')
            .prefetch_related()
            .get(
                Q(content__pk=pk) & 
                model_helpers.get_map_privacy_filters(user)
            )
        )
    except Exception as e:
        print(e)
        map_instance = None

    if map_instance:
        return render(request, 'library/map.html', {
            'map':map_instance, 
            'role':map_instance.get_role(user)}
        )

    messages.error(request, 'Page not found. You have been redirected to the library.', 'map-floating-message')
    return redirect('library:index')