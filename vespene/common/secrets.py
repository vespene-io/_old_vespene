#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  secrets.py - cloaks and decloaks secrets
#  --------------------------------------------------------------------------

from vespene.common.plugin_loader import PluginLoader

class SecretsManager(object):

    HEADER = "[VESPENE-CLOAK]"

    def __init__(self):
        self.plugin_loader = PluginLoader()
        self.plugins = self.plugin_loader.get_secrets_plugins()

    def is_cloaked(self, msg):
        if not msg:
            return False
        return msg.startswith(self.HEADER)

    def decloak(self, msg):
        if not self.is_cloaked(msg):
            return msg
        else:
            for plugin in self.plugins:
                if plugin.recognizes(msg):
                    return plugin.decloak(msg)
            raise Exception("no plugin found to decloak value")

    def cloak(self, msg):
        if not msg or self.is_cloaked(msg) or len(self.plugins) == 0:
            return msg
        return self.plugins[0].cloak(msg)
    
