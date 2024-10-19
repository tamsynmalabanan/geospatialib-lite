from django.shortcuts import redirect, render
from django.urls import resolve

class RedirectCancelledSocialLogin:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(request.path, resolve(request.path).app_name, resolve(request.path).url_name)
        if resolve(request.path).url_name == 'socialaccount_login_cancelled':
            return redirect('library:index')
        response = self.get_response(request)
        return response