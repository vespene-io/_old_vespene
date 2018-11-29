#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0

import glob
import os.path
import shutil
from datetime import datetime, timedelta

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# from vespene.models.project import Project
from vespene.models.build import Build
from vespene.common.logger import Logger

LOG = Logger()

class Command(BaseCommand):
    help = 'Removes old builds and buildroots'

    def add_arguments(self, parser):
        
        parser.add_argument(
            '--remove-builds',
            action='store_true',
            dest='remove_builds',
            help='If set, clean up old builds',
        )
        parser.add_argument(
            '--remove-build-roots',
            action='store_true',
            dest='remove_build_roots',
            help='If set, clean up old build roots',
        )
        parser.add_argument(
            '--days',
            dest='days',
            help='Cleanup items older than this many days',
            default=-1,
        )

    def handle(self, *args, **options):

        
        remove_builds = options['remove_builds']
        remove_build_roots = options['remove_build_roots']
        days = int(options['days'])

        if not remove_builds and not remove_build_roots:
            raise CommandError("expecting at least one of: --remove-builds or --remove-build-roots")
        if days < 0:
            raise CommandError("--days is required")

        threshold = datetime.now(tz=timezone.utc) - timedelta(days=days)
        timestamp = threshold.timestamp()

        if remove_build_roots:
            build_root = settings.BUILD_ROOT
            if not os.path.exists(build_root):
                raise CommandError("BUILD_ROOT as configured in settings (%s) does not exist on this node" % build_root)
            contents = glob.glob(os.path.join(build_root, "*"))
            count = 0
            for dirname in contents:
                if os.path.isdir(dirname):
                    mtime = os.path.getmtime(dirname)
                    if mtime < timestamp:
                        count = count + 1
                        shutil.rmtree(dirname)
            print("Deleted %d build roots" % count)

        if remove_builds:
            builds = Build.objects.filter(
                queued_time__gt = threshold
            )
            count = builds.count()
            builds.delete()
            print("Deleted %d builds" % count)


