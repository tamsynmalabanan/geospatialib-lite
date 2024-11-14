from django.shortcuts import redirect, render
from django.urls import resolve
from django.contrib import messages

class RedirectCancelledSocialLogin:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if resolve(request.path).url_name == 'socialaccount_login_cancelled':
            return redirect('library:index')
        response = self.get_response(request)
        return response