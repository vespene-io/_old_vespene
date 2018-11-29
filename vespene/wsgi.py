#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  wsgi.py - standard wsgi entry point generated from Django. Not used if
#  running the default webserver.
#  --------------------------------------------------------------------------

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vespene.settings")

application = get_wsgi_application()
