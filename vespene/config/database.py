#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
# ---------------------------------------------------------------------------
# database.py: database settings
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
# ---------------------------------------------------------------------------

# no passwords is specified in particular file and it doesn't matter
# this will almost certaintly be overridden by the setup process
# and only serves as a reference

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vespene',
        'HOST': 'localhost',
        'ATOMIC_REQUESTS': True
    }
}