#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  triggers.py - triggers are plugins that are run when certain things happen,
#  like when a build starts, or stops successfully or unsuccessfully. Triggers
#  are plugins - the basic command trigger can execute arbitrary CLI commands.
#  --------------------------------------------------------------------------

from vespene.models.build import SUCCESS
from vespene.common.plugin_loader import PluginLoader

# =========================================================

class TriggerManager(object):

    """
    Trigger manager handles activation of pre and post build
    triggers.
    """

    # -----------------------------------------------------

    def __init__(self, builder, build):
        """
        Constructor takes a build reference.
        """
        self.builder = builder
        self.build = build

        self.plugin_loader = PluginLoader()
        self.pre_trigger_plugins = self.plugin_loader.get_pre_trigger_plugins()
        self.success_trigger_plugins = self.plugin_loader.get_success_trigger_plugins()
        self.failure_trigger_plugins = self.plugin_loader.get_failure_trigger_plugins()

    # -----------------------------------------------------

    def run_all_pre(self):
        """
        Run all pre hooks - which can be scripts
        that simply take command line flags or recieve
        more detail on standard input. See docs for details.
        """
        self.build.append_message("----------\nPre hooks...")
        context = self.pre_context()
        for plugin in self.pre_trigger_plugins:
            plugin.execute_hook(self.build, context)

    # -----------------------------------------------------

    def run_all_post(self):
        """
        Similar to post hooks, pre hooks can be set to run
        only on success or failure.
        """
        self.build.append_message("----------\nPost hooks...")
        context = self.post_context()

        if self.build.status == SUCCESS:
            for plugin in self.success_trigger_plugins:
                plugin.execute_hook(self.build, context)

        else:
            for plugin in self.failure_trigger_plugins:
                plugin.execute_hook(self.build, context)

    # -----------------------------------------------------

    def pre_context(self):
        """
        This dictionary is passed as JSON on standard
        input to pre hooks.
        """
        return dict(
            hook='pre',
            build=self.build,
            project=self.build.project
        )

    # -----------------------------------------------------

    def post_context(self):
        """
        This dictionary is passed as JSON on standard
        input to post hooks.
        """
        return dict(
            hook='post',
            build=self.build,
            project=self.build.project
        )
