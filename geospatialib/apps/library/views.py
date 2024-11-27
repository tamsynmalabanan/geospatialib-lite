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

