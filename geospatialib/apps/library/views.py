from django.shortcuts import render, HttpResponse

from . import forms

def index(request):
    form = forms.SearchForm(data=request.GET)
    return render(request, 'library/index.html', {'form':form})