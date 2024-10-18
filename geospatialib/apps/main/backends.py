from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Q

User = get_user_model()

class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            username = kwargs.get('email', None)

        try:
            user_query = Q(**{'username__iexact':username}) | Q(**{'email__iexact':username})
            user = User.objects.get(user_query)
        except User.DoesNotExist:
            raise PermissionDenied("Invalid login credentials.")
        except User.MultipleObjectsReturned:
            raise PermissionDenied("Multiple users found with given credentials.")

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        else:
            raise PermissionDenied("Invalid login credentials.")

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None