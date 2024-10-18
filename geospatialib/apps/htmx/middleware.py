from django.shortcuts import redirect, render
from django.urls import resolve

class HTMXDomainRestriction:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if resolve(request.path).app_name == 'htmx' and not request.headers.get('HX-Request'):
            return redirect('library:index')
        response = self.get_response(request)
        return response