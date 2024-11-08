from django.contrib.auth.views import LogoutView
from django.urls import path, re_path

from . import views

app_name = 'hx_library'

urlpatterns = [
    path('search/', views.SearchList.as_view(), name='search'),
    path('share_dataset/', views.share_dataset, name='share_dataset'),
    path('cors_proxy/', views.cors_proxy, name='cors_proxy'),
]