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

mkdir -p /etc/vespene/settings.d/

cd /opt/vespene
echo $PYTHON
$PYTHON manage.py generate_secret

# application database config
cat >/etc/vespene/settings.d/database.py <<END_OF_DATABASES
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

# worker configuration settings
cat > /etc/vespene/settings.d/workers.py << END_OF_WORKERS
BUILD_ROOT="$BUILD_ROOT"
# FILESERVING_ENABLED = True
# FILESERVING_PORT = 8000
# FILESERVING_HOSTNAME = "this-server.example.com"
END_OF_WORKERS

# ui settings
cat > /etc/vespene/settings.d/interface.py << END_OF_INTERFACE
BUILDROOT_WEB_LINK="$BUILDROOT_WEB_LINK"
END_OF_INTERFACE

# apply database tables
# this only has to be run once but won't hurt anything by doing
# it more than once. You also need this step during upgrades.
cd /opt/vespene
$PYTHON manage.py migrate

