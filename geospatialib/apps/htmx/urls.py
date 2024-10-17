from django.contrib.auth.views import LogoutView
from django.urls import path, re_path

from . import views

app_name = 'htmx'

urlpatterns = [
    # path('', views.index, name='login'),
]