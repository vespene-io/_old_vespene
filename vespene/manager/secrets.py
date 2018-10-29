#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  secrets.py - uses plugins to symetrically encrypt/decrypt content
#  in the database. All plugins in the configuration can be used to 
#  decode data (if they match), but only the first plugin the settings
#  configuration will be used to encode.
#  --------------------------------------------------------------------------

from vespene.common.logger import Logger
from vespene.common.plugin_loader import PluginLoader

LOG = Logger()

HEADER = "[VESPENE-CLOAKED]"

class SecretsManager(object):

    def __init__(self):
        self.plugin_loader = PluginLoader()
        self.plugins = self.plugin_loader.get_secrets_plugins()

    def cloak(self, msg):
        if len(self.plugins) == 0:
            return msg
        if not self.is_cloaked(msg):
            return self.plugins[0].cloak(msg)
        else:
            # already cloaked, will not re-cloak
            return msg

    def is_cloaked(self, msg):
        return msg.startswith(HEADER)

    def decloak(self, msg):
        remainder = msg.replace(HEADER, "", 1)
        for plugin in self.plugins:
            if plugin.recognizes(remainder):
                return plugin.decloak(remainder)
        return remainder
