#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  slack.py - this is a plugin that sends slack notifications when builds
#  start or finish. It could easily be copied to add support for HipChat
#  or IRC, and contributions of those modules would be fantastic. Extensions
#  to move the configuration strings out of this file, and support more features
#  of Slack are also welcome.
#  --------------------------------------------------------------------------

from slackclient import SlackClient

from vespene.common.logger import Logger
from vespene.models.build import SUCCESS
from vespene.common.templates import template

LOG = Logger()

PRE_TEMPLATE = "Vespene Build {{ build.id }} for project \"{{ build.project.name }}\" started"
SUCCESS_TEMPLATE = "Vespene Build {{ build.id }} for project \"{{ build.project.name }}\" succeeded"
FAILURE_TEMPLATE = "Vespene Build {{ build.id }} for project \"{{ build.project.name }}\" failed"

class Plugin(object):

    def __init__(self, args):
        self.params = args
        self.channel = self.params['channel']
        self.token = self.params['token']
        self.client = SlackClient(self.token)

    def execute_hook(self, build, context):

        LOG.debug("executing slack hook")

        if context['hook'] == 'pre':
            slack_template = PRE_TEMPLATE
        elif build.status == SUCCESS:
            slack_template = SUCCESS_TEMPLATE
        else:
            slack_template = FAILURE_TEMPLATE

        msg = template(slack_template, context, strict_undefined=True)

        self.client.api_call("chat.postMessage", channel=self.channel, text=msg)
