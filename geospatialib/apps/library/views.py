from django.shortcuts import render
from django.core.paginator import Paginator

from . import forms, models
from htmx.hx_library.views import SearchList

import json

def index(request):
    form = forms.SearchForm(data=request.GET)
    return render(request, 'library/index.html', {'form':form})

def map(request):
    pass