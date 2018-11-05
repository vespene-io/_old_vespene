#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  webhooks.py - implementation of webhook support.  Right now this isn't
#  pluggable and contains an implementation tested for GitHub and some
#  code that *probably* works for GitLab. Upgrades welcome.
#  --------------------------------------------------------------------------

import json
from vespene.common.logger import Logger
from vespene.manager.jobkick import start_project
from vespene.models.project import Project

LOG = Logger()

# ===============================================================================================

class Webhooks(object):

    def __init__(self, request, token):

        body = request.body.decode('utf-8')
        self.token = token
        self.content = json.loads(body)

    def handle(self):
        """
        Invoked by views.py, recieves all webhooks and attempts to find out what
        projects correspond with them by looking at the repo.  If the project
        is webhook enabled, it will create a QUEUED build for that project.
        """

        # FIXME: at some point folks will want to support testing commits on branches
        # not set on the project.  This is a good feature idea, and to do this we
        # should add a webhooks_trigger_any_branch type option, that creates a build
        # with any incoming branch specified. 

        qs = Project.objects.filter(webhook_enabled=True)

        possibles = []

        # this fuzzy code looks for what may come in for webhook JSON for GitHub and GitLab
        # extension to support other SCM webhooks is welcome.
        for section in [ 'project', 'repository' ]:
            if section in self.content:
                for key in [ 'git_url', 'ssh_url', 'clone_url', 'git_ssh_url', 'git_http_url' ]:
                    repo = self.content[section].get(key, None)
                    if repo is not None:
                        possibles.append(repo)

        # find projects that match repos we have detected
        qs = Project.objects.filter(webhook_enabled=True, repo_url__in=possibles).all()
        for project in qs.all():
            if project.webhook_token is None or project.webhook_token == self.token:
                LOG.info("webhook starting project: %s" % project.id)
                if project.repo_branch is not None:
                    ref = self.content.get('ref')
                    if ref:
                        branch = ref.split("/")[-1]
                        # if the project selects a particular branch and this repo is for
                        # a different branch, we'll ignore the webhook. Otherwise we'll
                        # assume there is only one branch.  This could result in too many
                        # builds - if we add special handling, we should consider SVN
                        # doesn't really have branches
                        if project.repo_branch and branch and branch != project.repo_branch:
                            LOG.info("skipping, references another branch")
                            continue
                start_project(project)
