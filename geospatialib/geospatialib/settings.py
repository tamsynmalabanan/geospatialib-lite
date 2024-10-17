"""
Django settings for geospatialib project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os

if os.name == 'nt':
    VENV_BASE = os.environ['VIRTUAL_ENV']
    os.environ['PATH'] = os.path.join(VENV_BASE, 'Lib\\\\site-packages\\\\osgeo') + ';' + os.environ['PATH']
    os.environ['PROJ_LIB'] = os.path.join(VENV_BASE, 'Lib\\\\site-packages\\\\osgeo\\\\data\\\\proj') + ';' + os.environ['PATH']

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--!^$7x&a6b$0lbvp!z8tw*&@a%wtqe)*%_f@_sdf3%0a-zv$g9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    # '127.0.0.1',
    # '192.168.1.6',
    # 'geospatialib.com',
    # 'www.geospatialib.com',
]

AUTH_USER_MODEL = 'main.User'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # postgres
    'django.contrib.postgres',
    
    # gis
    'django.contrib.gis',

    # utils
    'tags',

    # local apps
    'apps.htmx',
    'apps.main',
    'apps.library',

    # 3rd-party apps
    'widget_tweaks',
    'leaflet',
    'django_htmx',
    'debug_toolbar',
]

LEAFLET_CONFIG = {
    'TILES': [],
    'DEFAULT_CENTER': (45, 0),
    'DEFAULT_ZOOM': 2,
    'MIN_ZOOM': 1,
    'MAX_ZOOM': 20,
    'DEFAULT_PRECISION': 6,
    'RESET_VIEW': False,
    'NO_GLOBALS': False,
    'SCALE': None,
    'PLUGINS': {
        'geocoder': {
            'css': [
                'https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.css', 
            ],
            'js': [
                'https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js'
            ],
            'auto_include': True,
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 3rd party
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_htmx.middleware.HtmxMiddleware',

]

ROOT_URLCONF = 'geospatialib.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR,],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'geospatialib.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "geospatialib-lite",
        "USER": "geospatialib",
        "PASSWORD": "geospatialib",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

# NOTE: 
# Create postgis extension in database
# pip install pipwin
# pip install psycopg2
# pipwin install gdal 
# https://github.com/ranjanport/GDAL/releases

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
