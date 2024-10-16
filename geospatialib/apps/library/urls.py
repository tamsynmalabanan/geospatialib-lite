from django.contrib.auth.views import LogoutView
from django.urls import path, re_path

from . import views

app_name = 'library'

urlpatterns = [
    path('', views.index, name='login'),
]