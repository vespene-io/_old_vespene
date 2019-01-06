#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  git.py - code for working with git.  To avoid surprising API breakage
#  and also to allow easier future features, this just runs the git CLI
#  versus using any git python libraries.
#  --------------------------------------------------------------------------

import os
import shlex

from vespene.common.logger import Logger
from vespene.workers import commands

LOG = Logger()

GIT_TYPES = [ "git://", "git+ssh://", "ssh://", "https://", "http://" ]

class Plugin(object):

    def __init__(self):
        pass

    def setup(self, build):
        # Basic constructor, takes a build, also tries to add the username if set to the repo URL.
        self.build = build
        self.project = build.project
        self.repo = build.project.repo_url
        self.repo = self._fix_scm_url()

    def get_revision(self):
        # Implementation of revision lookup for git
        cmd = "(cd %s; git rev-parse --short HEAD)" % self.build.working_dir
        out = commands.execute_command(self.build, cmd, output_log=False, message_log=True)
        return out.split("\n")[0].strip()

    def get_last_commit_user(self):
        # Implementation of last commit user lookup for git
        cmd = "(cd %s; git --no-pager log -n 1 --abbrev-commit --format='%s')" % (self.build.working_dir, '%aE')
        out = commands.execute_command(self.build, cmd, output_log=False, message_log=True)
        return out.split("\n")[0].strip()

    def checkout(self):
        # Git checkout implementation.
        self.build.append_message("----------\nCloning repository...")

        # TODO: may need to make SSH options more configurable, possibly using settings file?
        answer_file = None
        ask_pass = ""
        key_mgmt = dict()

        if self.repo.startswith("http://") or self.repo.startswith("https://"):
            # if using a http repo and a scm login password is set, tell git to execute
            # a file to retrieve the password
            if self.project.scm_login and self.project.scm_login.password is not None:
                answer_file = commands.answer_file(self.project.scm_login.get_password())
                ask_pass = " --config core.askpass=\"%s\"" % answer_file
            else:
                # it's not set, we can avoid an error if it asks for a password and
                # we have ALREADY added the username to the URL if we could, but if not
                # there's a slim chance this could go interactive on OS X laptops. See
                # development setup docs for how to turn this off.
                ask_pass = " --config core.askpass=''"
        else:
            # if using SSH, there's a chance we haven't seen the repo before, and need to be cool about it.
            # TODO: we may allow people to turn this off by adding this as a setting default.
            key_mgmt = {
               "GIT_SSH_COMMAND" : "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no",
            }

            if not self.project.ssh_keys.count():
                raise Exception("add one or more SSH keys to the project or use a http:// or https:// URL")

        branch_spec = ""
        if self.project.repo_branch:
            branch_spec = "--depth 1 -b %s --single-branch " % shlex.quote(self.project.repo_branch)

        recursive = ""
        if self.project.recursive:
            recursive = " --recursive "

        try:
            # run it
            cmd = "git clone %s%s %s%s %s -v" % (branch_spec, shlex.quote(self.repo), self.build.working_dir, recursive, ask_pass)
            # we should be a BIT smarter than this, but for now use the timeout command to kill the build if the SSH
            # unlock password or something might be wrong. We can modifiy this later to have watch phrases
            # that kill the command automatically when we see certain output.
            output = commands.execute_command(self.build, cmd, output_log=False, message_log=True, timeout=600, env=key_mgmt)
        finally:
            # delete the answer file if we had one
            if answer_file:
                os.remove(answer_file)

        return output
    
    def _fix_scm_url(self):
        # Adds the username and password into the repo URL before checkout, if possible
        # This isn't needed if we are using SSH keys, and that's already handled by SshManager
        
        scm_login = self.project.scm_login
        if scm_login:
            username = scm_login.username
            if "@" not in self.repo:
                for prefix in GIT_TYPES:
                    if self.repo.startswith(prefix):
                        repo = self.repo.replace(prefix, "")
                        return "%s%s@%s" % (prefix, username, repo)

        return self.repo
