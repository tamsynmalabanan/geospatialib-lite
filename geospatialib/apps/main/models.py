from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    
    def create_user(self, email, username=None, password=None, **kwargs):
        if not email:
            raise ValueError("User must have an email address.")
        email = self.normalize_email(email)

        user = self.model(email=email, username=username, **kwargs)
        user.set_password(password)
        user.save()
        
        return user
    
    def create_superuser(self, email, username=None, password=None, **kwargs):
        if password is None:
            raise ValueError('Password is required.')
        
        status_fields = ['is_active', 'is_staff', 'is_superuser']
        for field in status_fields:
            kwargs.setdefault(field, True)        
            if kwargs.get(field) is not True:
                raise ValueError(f'Field "{field}" must be set as True.')
        
        return self.create_user(email, username, password, **kwargs)
    

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Email', unique=True)
    username = models.SlugField('Username', unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']