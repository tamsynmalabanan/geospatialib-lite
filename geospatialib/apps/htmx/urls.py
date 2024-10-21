from django.contrib.auth.views import LogoutView
from django.urls import path, re_path

from . import views

app_name = 'htmx'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('user_account/<str:name>/', views.user_account, name='user_account'),
    path('password_validation/', views.password_validation, name='password_validation'),
    path('new_dataset/', views.new_dataset, name='new_dataset'),
]