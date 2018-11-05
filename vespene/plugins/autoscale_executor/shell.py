#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -----------------------------------------------------
#  autoscales a worker pool using determined parameters

import subprocess
import sys
from vespene.common.logger import Logger
from vespene.common.templates import template

LOG = Logger()

class Plugin(object):

    def __init__(self):
        pass

    def invoke(self, worker_pool, cmd):
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, shell=True, universal_newlines=True) as p:
            for line in p.stdout:
                LOG.debug("%s | %s" % (worker_pool.name, line))
        if p.returncode != 0:
            raise CalledProcessError(p.returncode, p.args)
           
    def scale_worker_pool(self, worker_pool, parameters):
        """
        This plugin just templates out a shell string using Jinja2 and runs it.
        See web docs at docs.vespene.io for an example.
        """

        cmd = worker_pool.executor_command
        cmd = template(cmd, parameters, strict_undefined=True)
        result = self.invoke(worker_pool, cmd)
        LOG.debug(result)


