#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  builder.py - the BuildLord class contains all the logic for running builds
#  once they have been queued by jobkick.py (on the view side) and picked
#  up by a worker (daemon.py).
#  --------------------------------------------------------------------------

import datetime
import traceback
import os

from django.conf import settings
from django.utils import timezone

from vespene.workers.ssh_agent import SshAgentManager
from vespene.workers.scm import ScmManager
from vespene.workers.triggers import TriggerManager
from vespene.workers.pipelines import PipelineManager
from vespene.workers.isolation import IsolationManager
from vespene.workers.registration import RegistrationManager
from vespene.workers import commands
from vespene.common.logger import Logger
from vespene.models.build import SUCCESS, FAILURE, RUNNING

LOG = Logger()

# =============================================================================

class BuildLord(object):

    def __init__(self, build):
        """
        Creates a build manager for a given build.
        """
        
        self.build = build
        self.project = self.build.project
        self.ssh_manager = SshAgentManager(self, self.build)
        self.scm_manager = ScmManager(self, self.build)
        self.trigger_manager = TriggerManager(self, self.build)
        self.pipeline_manager = PipelineManager(self, self.build)
        self.isolation_manager = IsolationManager(self, self.build)
        self.registration_manager = RegistrationManager(self, self.build)


    # -------------------------------------------------------------------------

    def main(self):
        """
        Main body of build process.
        """

        self.build.start_time = datetime.datetime.now(tz=timezone.utc)
        self.build.status = RUNNING
        self.build.save()
        self.registration_manager.go()

        if self.build.output is None:
            self.build.output = ""

        self.assign_working_dir()
        self.ssh_manager.add_all_keys()
        self.trigger_manager.run_all_pre()

        if self.project.repo_url:
            self.checkout_and_record_scm_info()

        self.run_build_script()
        
    # -------------------------------------------------------------------------

    def checkout_and_record_scm_info(self):
        """
        Perform a Source Control checkout and record the user and revision.
        """
        output = self.scm_manager.checkout() 
        self.build.append_output(output)
        self.build.revision_username = self.scm_manager.get_last_commit_user()
        self.build.revision = self.scm_manager.get_revision()

    # -------------------------------------------------------------------------

    def run_build_script(self):
        """
        Save the content of the build script to a directory inside the build dir.
        Execute the script from that directory, and save the output.
        """

        self.isolation_manager.begin()
        self.isolation_manager.execute()
        self.isolation_manager.end()

    # -------------------------------------------------------------------------

    def assign_working_dir(self):
        """
        Determine a temporary build directory for this build and create it.
        """

        # TODO: this isn't cross platform yet but is seemingly more reliable than 'os' functions on OS X
        # will need to detect the platform and make the appropriate changes for Windows.
        path = os.path.join(settings.BUILD_ROOT, str(self.build.id))
        commands.execute_command(self.build, "mkdir -p %s" % path)
        commands.execute_command(self.build, "chmod 770 %s" % path)
        self.build.working_dir = path
        self.build.save()
        return path

    # -------------------------------------------------------------------------

    def flag_build_successful(self):
        """
        Record a successful build.
        """

        LOG.debug("flagging build as successful")
        self.build.status = SUCCESS
        self.build.save()
        self.project.last_successful_build = self.build
        self.project.save(update_fields=['last_successful_build'])

    # -------------------------------------------------------------------------

    def flag_build_failure(self, e):
        """
        Record a failed build.
        """

        LOG.debug("flagging build as failure")
        self.build.append_output(str(e))
        self.build.status = FAILURE
        self.build.save()

    # -------------------------------------------------------------------------

    def flag_build_done(self):
        """
        Whether successful or not, finish recording the build.
        """

        LOG.debug("flagging build as done")
        self.project.last_build = self.build
        self.build.end_time = datetime.datetime.now(tz=timezone.utc)
        self.project.active_build = None
        self.project.save(update_fields=['last_build', 'active_build'])


    # -------------------------------------------------------------------------

    def go(self):
        """
        Run the build process, catching any errors that may occur.
        """

        try:

            self.main()
            self.flag_build_successful()

        except Exception as e:

            LOG.error("an error occurred")
            traceback.print_exc()
            self.build.status = FAILURE
            if self.build.return_code is None:
                self.build.return_code = -1
            self.flag_build_failure(e)

        finally:

            self.flag_build_done()
            self.trigger_manager.run_all_post()

        if self.build.status == SUCCESS:
            self.pipeline_manager.go()

 
