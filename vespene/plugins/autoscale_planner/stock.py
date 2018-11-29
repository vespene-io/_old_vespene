#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -----------------------------------------------------
#  calculates how large an autoscaling group for a worker should be

from django.utils import timezone
from datetime import datetime, timedelta

from vespene.common.logger import Logger
from vespene.common.templates import template
from vespene.models.build import Build, QUEUED, RUNNING

import math
import os.path
import json

LOG = Logger()


class Plugin(object):

    def __init__(self):
        pass

    def is_time_to_adjust(self, worker_pool):
        """
        Determine if it is time to re-evaluate the autoscaling status of this pool
        """

        last = worker_pool.last_autoscaled
        if last is None:
            return True
        now = datetime.now(tz=timezone.utc)
        threshold = now - timedelta(minutes=worker_pool.reevaluate_minutes)
        result = (worker_pool.last_autoscaled > threshold)
        return result


    def formula(self, worker_pool, x, y):
        """
        Apply calculations using weights to return actual desired sizes
        """

        count = x + y
        count = math.ceil(count * worker_pool.multiplier) + worker_pool.excess
        if count < worker_pool.minimum:
            count = worker_pool.minimum
        if count > worker_pool.maximum:
            count = worker_pool.maximum
        return count

    def get_parameters(self, worker_pool):
        """
        Get the desired-size parameters for the execution plugin
        """

        running = Build.objects.filter(
            status = RUNNING,
            worker_pool = worker_pool
        ).count()

        if worker_pool.build_latest:
            queued = Build.objects.filter(
                worker_pool = worker_pool,
                status = QUEUED,
            ).distinct('project').count()
        else:
            queued = Build.objects.filter(
                worker_pool = worker_pool,
                status = QUEUED,
            ).count()

        return dict(
            worker_pool = worker_pool,
            # number of additional worker images that should be spun up 
            # use this if the provisioning system is NOT declarative
            queued_size = self.formula(worker_pool, queued, running),
            # total number of worker images that should be spun up total
            # use this if the provisioning system IS declarative
            size = self.formula(worker_pool, queued, 0),
        )



     

