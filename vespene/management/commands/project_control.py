#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#---------------------------------------------------------------------------
# project_control.py - CLI command that can start or stop projects.  This is 
# mostly used for development testing and can be upgraded.
#---------------------------------------------------------------------------

from django.core.management.base import BaseCommand, CommandError
from vespene.models.project import Project
from vespene import jobkick
from vespene.common.logger import Logger

LOG = Logger()

class Command(BaseCommand):
    help = 'Starts and stops builds for a given project'

    def add_arguments(self, parser):
        parser.add_argument('project', type=int, help='project id')
        
        parser.add_argument(
            '--start',
            action='store_true',
            dest='start',
            help='Start a build for this project',
        )
        parser.add_argument(
            '--stop',
            action='store_true',
            dest='stop',
            help='Stop a build for this project',
        )

    def handle(self, *args, **options):

        
        project_id = options['project']
        start = options['start']
        stop = options['stop']

        project = Project.objects.get(id=project_id)
        
        if not start and not stop:
            raise CommandError("either --start or --stop are required")
        if stop and start:
            raise CommandError("--start and --stop are mutually exclusive")
        elif start:   
            LOG.info("Starting project")
            jobkick.start_project(project)
        else:
            LOG.info("Stopping project")
            jobkick.stop_project(project)
