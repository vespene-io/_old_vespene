#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  github.py - plumbing for supporting GitHub within the Vespene
#  organizational imports feature
#  --------------------------------------------------------------------------

import os
import shlex

from django.db.models import Q
from github import Github

from vespene.common.logger import Logger
from vespene.workers import commands

LOG = Logger()

class Plugin(object):

    def __init__(self, parameters=None):
        self.parameters = parameters
        if parameters is None:
            self.parameters = {}

    def get_handle(self, organization):
        scm_login = organization.scm_login
        if organization.api_endpoint:
            g = Github(scm_login.username, scm_login.password(), base_url=organization.api_endpoint)
        else:
            g = Github(scm_login.username, scm_login.get_password())
        return g

    def find_all_repos(self, organization, build):
        handle = self.get_handle(organization)
        org = handle.get_organization(organization.organization_identifier)
        repos = org.get_repos(type='all')
        results = []
        for repo in repos:
            results.append(repo.clone_url)
        return results

    def clone_repo(self, organization, build, repo, count):

        # much of code is borrowed from plugins.scm.git - but adapted enough that
        # sharing is probably not worthwhile. For instance, this doesn't have
        # to deal with SSH checkouts.

        build.append_message("cloning repo...")

        repo = self.fix_scm_url(repo, organization.scm_login.username)
        answer_file = commands.answer_file(organization.scm_login.get_password())
        ask_pass = " --config core.askpass=\"%s\"" % answer_file
        branch_spec = "--depth 1 --single-branch "

        clone_path = os.path.join(build.working_dir, str(count))

        try:
            # run it
            cmd = "git clone %s %s %s %s" % (shlex.quote(repo), clone_path, ask_pass, branch_spec)
            output = commands.execute_command(build, cmd, output_log=False, message_log=True)
        finally:
            # delete the answer file if we had one
            os.remove(answer_file)

        return clone_path
    
    def fix_scm_url(self, repo, username):

        # Adds the username and password into the repo URL before checkout, if possible
        # This isn't needed if we are using SSH keys, and that's already handled by SshManager
        
        for prefix in [ 'https://', 'http://' ]:
            if repo.startswith(prefix):
                repo = repo.replace(prefix, "")
                return "%s%s@%s" % (prefix, username, repo)
        return repo

