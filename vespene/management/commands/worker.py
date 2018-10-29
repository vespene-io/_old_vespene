#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#---------------------------------------------------------------------------
# worker.py - this is the management command that starts worker processes
# that work a given queue, and is typically involved by supervisor, configured
# in /etc/vespene/supervisord.conf
#---------------------------------------------------------------------------

from django.core.management.base import BaseCommand
from vespene.workers.daemon import Daemon



class Command(BaseCommand):
    help = 'Starts a daemon process for background jobs'

    def add_arguments(self, parser):
        parser.add_argument('queue', type=str, help='name of the queue, use \'general\' for the unassigned queue')

    def handle(self, *args, **options):        
        queue = options['queue']
        worker = Daemon(queue)
        worker.run()

        
