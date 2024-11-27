from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX

from urllib.parse import urlparse
import uuid

from random_username.generate import generate_username

from . import validators, choices
from utils.general import form_helpers

class UserManager(BaseUserManager):

    def username_is_available(self, username, user=None):
        user_query = self.model.objects.filter(username__iexact=username)
        if user and user.pk:
            user_query = user_query.exclude(pk=user.pk)
        return not user_query.exists()

    def generate_random_username(self, user=None):
        while True:
            username = slugify(generate_username(1)[0])
            if self.username_is_available(username, user):
                try:
                    validators.validate_username(username)
                    break
                except ValidationError:
                    continue
        return username.lower()

    def create_user(self, email, username=None, password=None, **kwargs):
        if not email:
            raise ValueError("User must have an email address.")
        email = self.normalize_email(email)

        if username and not self.username_is_available(username):
            raise ValueError('Username is not available.')
        if not username:
            username = self.generate_random_username()
        username = username.lower()

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
    username = models.SlugField('Username', unique=True, validators=[validators.validate_username])
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    dashboard_privacy = models.CharField('Dashboard', max_length=8, choices=form_helpers.dict_to_choices(choices.USER_PRIVACY), default='public')
    map_privacy = models.CharField('Map (default)', max_length=8, choices=form_helpers.dict_to_choices(choices.USER_PRIVACY), default='public')
    
    joined_on = models.DateTimeField('Join date', auto_now_add=True)
    first_name = models.CharField('First name', max_length=32, blank=True, null=True)
    last_name = models.CharField('Last name', max_length=32, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def proper_name(self):
        return ' '.join([self.first_name, self.last_name])

    @property
    def has_no_password(self):
        return self.password.startswith(UNUSABLE_PASSWORD_PREFIX)

    @property
    def has_no_first_name(self):
        return not self.first_name or self.first_name.strip() == ''
    

class Tag(models.Model):
    tag = models.CharField('Tag', max_length=64, unique=True)

    def __str__(self) -> str:
        return self.tag
    
    def save(self, *args, **kwargs):
        self.tag = self.tag.lower()
        super().save(*args, **kwargs)

class URL(models.Model):
    url = models.URLField('URL', max_length=255, unique=True)

    def __str__(self) -> str:
        return self.url

    @property
    def domain(self):
        return urlparse(self.url).netloc
    
class Content(gis_models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    added_by = models.ForeignKey("main.User", verbose_name='Added by', editable=False, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)ss_added')
    added_on = models.DateTimeField('Added on', auto_now_add=True)
    
    updated_by = models.ForeignKey("main.User", verbose_name='Updated by', editable=False, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)ss_updated')
    updated_on = models.DateTimeField('Updated on', auto_now=True)

    type = models.CharField('Type', choices=[('dataset','dataset'), ('map', 'map')], editable=False, max_length=8, default='dataset')
    dataset = models.OneToOneField("library.Dataset", verbose_name='Dataset', on_delete=models.CASCADE, related_name='content', blank=True, null=True, editable=False)
    map = models.OneToOneField("map.Map", verbose_name='Map', on_delete=models.CASCADE, related_name='content', blank=True, null=True, editable=False)

    label = models.CharField('Label', max_length=255, blank=True, null=True)
    abstract = models.TextField('Abstract', blank=True, null=True)
    tags = models.ManyToManyField("main.Tag", verbose_name='Tags', blank=True, related_name='contents')
    bbox = models.PolygonField('Bounding box', blank=True, null=True)

    def __str__(self) -> str:
        if self.label:
            return self.label
        return super().__str__()

    @property
    def instance(self):
        return getattr(self, self.type)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

