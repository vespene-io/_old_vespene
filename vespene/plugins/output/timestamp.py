#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  timestamp.py - an output plugin that appends the elapsed time before
#  log messages
#  --------------------------------------------------------------------------

from vespene.workers import commands
from vespene.common.logger import Logger
from datetime import datetime
from django.utils import timezone

LOG = Logger()

class Plugin(object):

    def __init__(self, parameters=None):
        if parameters is None:
            parameters = {}
        self.parameters = parameters
        self.mode = self.parameters.get('mode', 'elapsed')
        if self.mode != 'elapsed':
            raise Exception("the only available timestamp mode is 'elapsed'.")

    def filter(self, build, msg):
        if msg is None:
            return None
        now = datetime.now(tz=timezone.utc)
        delta = now - build.start_time
        minutes = delta.total_seconds() / 60.0
        prefix = "%0.2f" % minutes
        return "%sm | %s" % (prefix.rjust(8), msg)
