#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#---------------------------------------------------------------------------
# generate_supervisor.py - CLI command that is used by the setup shell
# scripts as mentioned in the web documentation to more easily generate
# a supervisord configuration that runs both the Vespene web server and
# any number of worker processes. For usage see setup/centos7/6_services.py.
#---------------------------------------------------------------------------

from django.core.management.base import BaseCommand, CommandError
from vespene.common.logger import Logger

import os

PREAMBLE = """
[supervisord]
childlogdir=/var/log/vespene/
logfile=/var/log/vespene/supervisord.log
logfile_maxbytes=50MB
logfile_backups=10
loglevel=info
pidfile=/var/run/supervisord.pid
nodaemon=false
minfds=1024
minprocs=200
"""

WEB = """
[program:server]
command=gunicorn %s vespene.wsgi 
process_name=%s
directory=%s
autostart=true
autorestart=false
redirect_stderr=true
stdout_logfile = /var/log/vespene/web.log
stdout_logfile_maxbytes=50MB
"""

WORKER = """
[program:worker_%s]
command=/usr/bin/ssh-agent %s manage.py worker %s
numprocs=%s
process_name=%s
directory=%s
autostart=true
autorestart=false
redirect_stderr=true
stdout_logfile = /var/log/vespene/worker_%s.log
stdout_logfile_maxbytes=50MB
"""

# USAGE: manage.py generate_supervisor --path /etc/vespene/supervisord.conf --workers "name1=2 name2=5" \
#        --executable `which python` --source=/opt/vespene --gunicorn "--bind 127.0.0.1:8000"
LOG = Logger()

class Command(BaseCommand):
    help = 'Configures supervisor for production deploys. See the setup/ directory for example usage'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='filename to write')
        parser.add_argument('--workers', type=str, help="what workers to run?")
        parser.add_argument('--executable', type=str, help="python executable")
        parser.add_argument('--source', type=str, help='source')
        parser.add_argument('--gunicorn', type=str, help='gnuicorn options string', default='--bind 127.0.0.1:8000')

    def handle(self, *args, **options):

        path = options.get('path', None)
        workers = options.get('workers', None)
        python = options.get('executable', None)
        source = options.get('source', None)
        gunicorn = options.get('gunicorn', None)

        if not workers and not "=" in workers:
            raise CommandError("worker configuration does not look correct")
        if not python or not os.path.exists(python):
            raise CommandError("--executable must point to an interpreter")
        
        workers = workers.split(" ")
        
        fd = open(path, "w+")
        fd.write(PREAMBLE)
        fd.write("\n")
        fd.write(WEB % (gunicorn, "%(program_name)s", source))
        fd.write("\n")

        for worker in workers:
            tokens = worker.split("=", 1)
            key = tokens[0]
            value = tokens[1]
            stanza = WORKER % (key, python, key, value, "%(program_name)s%(process_num)s", source, key)
            fd.write(stanza)
            fd.write("\n")
        
        fd.close()

