from django.contrib.auth.views import LogoutView
from django.urls import path, re_path

from . import views

app_name = 'hx_map'

urlpatterns = [
    path('create_map/', views.create_map, name='create_map'),
    path('edit_map/<int:pk>/<str:section>/', views.edit_map, name='edit_map'),
    path('map_privacy/', views.map_privacy, name='map_privacy'),
    path('tags_datalist/', views.tags_datalist, name='tags_datalist'),
]