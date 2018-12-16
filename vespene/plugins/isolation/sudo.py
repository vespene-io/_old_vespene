#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  sudo.py - this is a build isolation strategy that runs sudo to a configured
#  username prior to running a build.
#  --------------------------------------------------------------------------

from vespene.workers import commands
from vespene.common.logger import Logger

import os.path
import json
import shutil

LOG = Logger()

class Plugin(object):

    def __init__(self):
        pass

    def setup(self, build):
        self.build = build
        self.sudo_user = self._get_sudo_user()
        self.chmod = self._get_chmod()

    def _get_script_file_name(self):
        # Where should we write the build script?
        if not self.build.working_dir:
            raise Exception("working directory not set")
        return os.path.join(self.build.working_dir, "vespene_launch.sh")

    def _get_json_file_name(self):
        # Where should we write the build script?
        return os.path.join(self.build.working_dir, "vespene.json")

    def _get_sudo_user(self):
        # See if a sudo user is configured on the worker pool, if not, just use 'nobody'
        user = self.build.project.worker_pool.sudo_user
        if not user:
            return "nobody"
        return user

    def _get_chmod(self):
        # Check permissions hex and assert it is sane.
        chmod = self.build.project.worker_pool.permissions_hex
        if not chmod:
            chmod = 0x777
        chmod = int(chmod, 16)
        return "%X" % chmod

    def begin(self):

        self.build.append_message("running build asunder user: %s" % self.sudo_user)

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

    def end(self):
        # Chdir out of the build root
        os.chdir(self.prev_dir)

    def execute(self):
        self.build.append_message("----------\nBuilding...")
        commands.execute_command(self.build, "chmod -R %s %s" % (self.chmod, self.build.working_dir), output_log=False, message_log=True)
        commands.execute_command(self.build, "chmod a+x %s" % self.script_file_name, output_log=False, message_log=True)
        if shutil.which('timeout'):
            timeout = "timeout %d " % (self.build.project.timeout * 60)
        else:
            timeout = ""
        sudo_command = "sudo -Snk -u %s %s%s" % (self.sudo_user, timeout, self.script_file_name)
        self.build.append_message("see 'Output'")
        commands.execute_command(self.build, sudo_command, log_command=False, output_log=True, message_log=False)