#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
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
        parser.add_argument('--max-builds', dest="max_builds", type=int, help='if set, terminate after this many builds', default=-1)
        parser.add_argument('--max-wait-minutes', dest="max_wait_minutes", type=int, help="if set, terminate after this many minutes of no queued builds", default=-1)
        parser.add_argument( '--build-id', dest="build_id", type=int, help='run only this one build ID then exit', default=-1)

        parser.add_argument('queue', type=str, help='name of the queue, use \'general\' for the unassigned queue')

    def handle(self, *args, **options):        
        queue = options['queue']
        max_wait_minutes = options['max_wait_minutes']
        max_builds = options['max_builds']
        build_id = options['build_id']
        worker = Daemon(queue,
                        max_builds=max_builds,
                        max_wait_minutes=max_wait_minutes,
                        build_id=build_id)
        worker.run()

        
