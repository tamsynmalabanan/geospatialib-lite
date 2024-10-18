from django.contrib.auth.views import LogoutView
from django.urls import path, re_path
from .views import *

app_name = 'main'

urlpatterns = [
    path('init/', init, name='init'),
]