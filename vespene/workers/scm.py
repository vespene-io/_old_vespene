#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  scm.py - encapsulates the logic of a SCM checkout. The implementation
#  for various source control providers is contained in 'plugins/scm'.
#  --------------------------------------------------------------------------

from vespene.common.logger import Logger
from vespene.common.plugin_loader import PluginLoader

LOG = Logger()

# =============================================================================

class ScmManager(object):

    def __init__(self, builder, build):
        self.builder = builder
        self.build = build
        self.project = self.build.project
        self.repo = self.project.repo_url
        self.scm_type = self.project.scm_type
        
        self.plugin_loader = PluginLoader()
        self.provider = self.get_provider()

    # -------------------------------------------------------------------------

    def get_provider(self):
        """
        Return the management object for the given repo type.
        """
        plugins = self.plugin_loader.get_scm_plugins()
        plugin = plugins.get(self.scm_type)
        if plugin is None:
            raise Exception("no scm plugin configurated for project scm type: %s" % self.scm_type)
        plugin.setup(self.build)
        return plugin

    # -------------------------------------------------------------------------

    def checkout(self):
        """
        Perform a checkout in the already configured build dir
        """
        self.provider.checkout()

    # -------------------------------------------------------------------------

    def get_revision(self):
        """
        Find out what the source control revision is.
        """
        return self.provider.get_revision()

    # -------------------------------------------------------------------------

    def get_last_commit_user(self):
        """
        Find out what user made the last commit on this branch
        """
        return self.provider.get_last_commit_user()  
