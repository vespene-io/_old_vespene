#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  isolation.py - when each build runs, it can be wrapped
#  in an isolation procedure to prevent the build from doing "too many
#  dangeorus things".  This logic is maintained in 'plugins/isolation' and
#  can include a simple sudo before execution or building inside a container.
#  --------------------------------------------------------------------------

from vespene.common.logger import Logger
from vespene.common.plugin_loader import PluginLoader

LOG = Logger()

# =============================================================================

class IsolationManager(object):

    def __init__(self, builder, build):
        self.builder = builder
        self.build = build
        self.project = self.build.project
        self.working_dir = self.build.working_dir
        self.isolation = self.project.worker_pool.isolation_method
        self.plugin_loader = PluginLoader()
        self.provider = self.get_provider()

    # -------------------------------------------------------------------------

    def get_provider(self):
        """
        Return the management object for the given repo type.
        """
        plugins = self.plugin_loader.get_isolation_plugins()
        plugin = plugins.get(self.isolation)
        if plugin is None:
            raise Exception("no isolation plugin configurated for worker pool isolation type: %s" % self.isolation)
        plugin.setup(self.build)
        return plugin

    # -------------------------------------------------------------------------

    def begin(self):
        """
        Begin isolation (chroot, container, sudo,  etc)
        """
        self.provider.begin()

    # -------------------------------------------------------------------------

    def execute(self):
        """
        Code that launches the build
        """
        return self.provider.execute()


    # -------------------------------------------------------------------------

    def end(self):
        """
        End isolation
        """
        return self.provider.end()
