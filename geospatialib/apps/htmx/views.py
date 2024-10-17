from django.shortcuts import render

from .. import library


def new_dataset(request):
    return render(request, 'library/new_dataset/form.html')
