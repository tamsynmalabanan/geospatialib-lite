from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import User

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.username = User.objects.generate_random_username()
        return user