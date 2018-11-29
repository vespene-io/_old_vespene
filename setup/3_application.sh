#!/bin/bash

# ---------------------------------------------------------------------------
# 3_application.sh: this step sets up Vespene configurations in /etc/vespene/settings.d, overriding
# some defaults.  It does not configure plugins, which are described in the online
# documentation, so you'll get the default plugin configuration to start.
# ---------------------------------------------------------------------------

# this step also makes sure database tables are present on the database server, which
# is set up by the previous script.

# load common settings
source ./0_common.sh

#---

cd /opt/vespene
echo $PYTHON
sudo $PYTHON manage.py generate_secret

#---

# application database config
sudo tee /etc/vespene/settings.d/database.py >/dev/null <<END_OF_DATABASES
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'vespene',
            'USER': 'vespene',
            'PASSWORD' : '$DBPASS',
            'HOST': '$DBSERVER',
            'ATOMIC_REQUESTS': True
        }
}
END_OF_DATABASES

#---

# worker configuration settings
sudo tee /etc/vespene/settings.d/workers.py >/dev/null << END_OF_WORKERS
BUILD_ROOT="${BUILDROOT}"
# FILESERVING_ENABLED = True
# FILESERVING_PORT = 8000
# FILESERVING_HOSTNAME = "this-server.example.com"
END_OF_WORKERS

#---

# ui settings
sudo tee /etc/vespene/settings.d/interface.py >/dev/null << END_OF_INTERFACE
BUILDROOT_WEB_LINK="${BUILDROOT_WEB_LINK}"
END_OF_INTERFACE

#---

# authentication settings
sudo tee /etc/vespene/settings.d/authentication.py >/dev/null << END_OF_AUTHENTICATION
# Vespene uses the standard Django authentication system
# the default authentication scheme uses the local database. to use LDAP:
#
# pip install python-ldap
# pip install django-auth-ldap
# 
# and uncomment these lines:
#
# import ldap
# from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

# then configure LDAP as follows:
# see example: https://django-auth-ldap.readthedocs.io/en/latest/example.html
#
# to enable LDAP authentication, uncomment django_auth_ldap.backend.LDAPBackend from AUTHENTICATION_BACKENDS.
# to use LDAP exclusively, comment out django.contrib.auth.backends.ModelBackend
#
# See also http://docs.vespene.io/authz.html

AUTHENTICATION_BACKENDS = (
    #'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
END_OF_AUTHENTICATION

#---

# ensure app user can read all of this
echo sudo chown -R $APP_USER /etc/vespene

#---

# apply database tables
# this only has to be run once but won't hurt anything by doing
# it more than once. You also need this step during upgrades.
cd /opt/vespene
$APP_SUDO $PYTHON manage.py migrate
