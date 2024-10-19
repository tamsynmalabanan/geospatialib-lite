from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from django.contrib import messages

from urllib.parse import urlparse, parse_qs

from .forms import AuthenticationForm

User = get_user_model()

# def init(request):
#     def create_superuser():
#         email='admin@geospatialib.com'
#         password='Eg73*WV#5f62kt'
#         username = 'geospatialib_admin'
#         user_query = User.objects.filter(email=email)
#         if user_query.exists():
#             user = user_query.first()
#             user.username = username
#             user.set_password(password)
#             user.save()
#         else:
#             User.objects.create_superuser(
#                 email=email,
#                 password=password,
#                 username=username
#             )
        
#         print('Created/reset superuser')

#     def setup_social_auth():
#         from django.contrib.sites.models import Site
#         from allauth.socialaccount.models import SocialApp

#         site = Site.objects.get(id=1)
#         site.domain = '127.0.0.1:8000'
#         site.name = '127.0.0.1:8000'
#         site.save()

#         app, created = SocialApp.objects.get_or_create(
#             provider='google',
#             name='Geospatialib',
#             client_id='1030296478700-cm9kv6n1qvh6q1icribvuthcbhatqlai.apps.googleusercontent.com',
#             secret='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',
#         )
#         if created:
#             app.sites.add(site)
            
#         print('Social auth setup')

#     create_superuser()
#     setup_social_auth()

#     return redirect('library:index')

