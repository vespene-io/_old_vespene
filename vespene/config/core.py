#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY INFO: these next two keys are NOT used in production, run
# 'make secrets' and this will generate a
# /etc/vespene/settings.d/security.py file to replace them. Read
# the online security docs for more info

SECRET_KEY = 'y1#h2iphta7==wf_9&!f4j%hrs@1kwc*nxe8-!ikfo$uyc7n$)'

# This key is one used by the 'fernet' library and to avoid
# confusion has NO value in this stock file.  Run 'make secrets'
# prior to execution or certain objects will not be able
# to be encrypted

SYMETRIC_SECRET_KEY = None

# TODO: make sure middleware logs all errors even in debug mode

DEBUG = True

# Django core logging settings

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'vespene'
]

from django.contrib.messages import constants as message_constants
MESSAGE_LEVEL = message_constants.DEBUG

CRISPY_TEMPLATE_PACK = 'bootstrap3'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vespene.views.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment' : 'vespene.common.templates.environment',
            'context_processors' : [
                'django_settings_export.settings_export'
            ]
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors' : [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ]
        }
    }
]

DEFAULT_PAGE_SIZE = 50

LOGIN_REDIRECT_URL = '/'

WSGI_APPLICATION = 'vespene.wsgi.application'

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC' # Never change this, date math will break!

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = STATIC_ROOT = os.path.join(BASE_DIR, 'static/')


LOG_LEVEL='DEBUG'

# you should not install Vespene to be publically accessible but
# if you do ignore that advice, change this to include internal domain
# like ".example.com"

ALLOWED_HOSTS = [ '*' ]

ALLOW_UI_USER_CREATION = True
ALLOW_UI_GROUP_CREATION = True

SETTINGS_EXPORT = [
    'ALLOW_UI_USER_CREATION',
    'ALLOW_UI_GROUP_CREATION'
]
