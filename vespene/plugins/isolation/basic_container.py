#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  basic_container.py - this is a docker-cli based isolation strategy
#  that runs builds as the result of a "docker build" command, and then
#  copies the build directory out of the resultant CLI image.  The docker
#  containers are short-lived and deleted after the build is done.
#  --------------------------------------------------------------------------

from vespene.workers import commands
from vespene.common.logger import Logger
from vespene.common.templates import template

import os.path
import json

LOG = Logger()

CONTAINER_TEMPLATE = """
FROM {{ container_base_image }}
ADD . /tmp/buildroot
RUN chmod +x /tmp/buildroot/vespene_launch.sh
RUN (cd /tmp/buildroot; timeout {{ timeout }} /tmp/buildroot/vespene_launch.sh)
ENTRYPOINT sleep 1000
"""

class Plugin(object):

    def __init__(self):
        pass

    def setup(self, build):
        self.build = build

    def _get_script_file_name(self):
        # Where should we write the build script?
        if not self.build.working_dir:
            raise Exception("working directory not set")
        return os.path.join(self.build.working_dir, "vespene_launch.sh")

    def _get_json_file_name(self):
        return os.path.join(self.build.working_dir, "vespene.json")

    def _get_container_base_image(self):
        if not self.build.project.container_base_image:
            raise Exception("container base image is not set")
        return self.build.project.container_base_image

    def begin(self):
        # Write the build script, the chdir into the build root.
        self.script_file_name = self._get_script_file_name()
        self.json_file_name = self._get_json_file_name()

        fh = open(self.script_file_name, "w")
        fh.write(self.build.script)
        fh.close()

        fh = open(self.json_file_name, "w")
        fh.write(self.build.variables)
        fh.close()

        self.prev_dir = os.getcwd()
        os.chdir(self.build.working_dir)

        base = self._get_container_base_image()

        self.build.append_message("using container base image: %s" % base)

        context = dict(
            timeout = (60 * self.build.project.timeout),
            container_base_image = base,
            buildroot = self.build.working_dir
        )
        contents = template(CONTAINER_TEMPLATE, context)
        
        fh = open("Dockerfile", "w")
        fh.write(contents)
        fh.close()

    def end(self):
        # Chdir out of the build root
        os.chdir(self.prev_dir)

    def execute(self):

        self.build.append_message("----------\nBuilding...")

        img = "vespene_%s" % self.build.id

        cmd = "docker build . -t %s" % img
        commands.execute_command(self.build, cmd, log_command=True, output_log=True, message_log=False)
        cmd = "docker run -d %s --name %s" % (img, img)
        commands.execute_command(self.build, cmd, log_command=True, output_log=True, message_log=False)
        cmd = "docker ps -a | grep %s" % img
        out = commands.execute_command(self.build, cmd, log_command=True, output_log=True, message_log=True)
        token = out.split("\n")[0].split(" ")[0]
        cmd = "docker cp %s:/tmp/buildroot ." % (token)
        commands.execute_command(self.build, cmd, log_command=True, output_log=False, message_log=True)
        cmd = "cp -r buildroot/* ."
        commands.execute_command(self.build, cmd, log_command=True, output_log=False, message_log=True)
        cmd = "rm -R buildroot"
        commands.execute_command(self.build, cmd, log_command=True, output_log=False, message_log=True)
        cmd = "docker container stop %s" % (token)
        commands.execute_command(self.build, cmd, log_command=True, output_log=False, message_log=True)
        cmd = "docker container rm %s" % (token)
        commands.execute_command(self.build, cmd, log_command=True, output_log=False, message_log=True)
        cmd = "docker image rm %s" % (img)
        commands.execute_command(self.build, cmd, log_command=True, output_log=False, message_log=True)

