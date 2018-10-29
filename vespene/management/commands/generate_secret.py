#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause

import sys
import os
import random
from cryptography import fernet
from django.core.management.base import BaseCommand
from vespene.common.logger import Logger

CONTENTS = """
DJANGO_SECRET_KEY = "%s"

SYMETRIC_SECRET_KEY = %s
"""

# /usr/bin/python36 manage.py supervisor_generate --path /etc/vespene/supervisord.conf --controller true --workers "name1=2 name2=5" --python /usr/bin/python36

LOG = Logger()

SECRETS = "/etc/vespene/settings.d/secrets.py"

def django_secret_key():
    return ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))

def symetric_secret_key():
    return fernet.Fernet.generate_key()

class Command(BaseCommand):
    help = 'Configures supervisor for production deploys. See the setup/ directory for example usage'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        if os.path.exists(SECRETS):
            print("WARNING: running this command again would render some secrets in the database unreadable")
            print("if you wish to proceed, delete %s manually first" % SECRETS)
            sys.exit(1)

        fd = open(SECRETS, "w+")
        s1 = django_secret_key()
        s2 = symetric_secret_key()
        fd.write(CONTENTS % (s1, s2))
        fd.close()



