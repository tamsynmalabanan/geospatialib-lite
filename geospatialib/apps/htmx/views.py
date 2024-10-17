from django.shortcuts import render

from .. import library


def new_dataset(request):
    return render(request, 'library/forms/new_dataset.html')
