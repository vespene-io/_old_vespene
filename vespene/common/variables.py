#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  variables.py - this encapsulates calls to the various 'variables' plugins
#  and is used to generate variables in 'vespene.json' (a file written into
#  each buildroot) as well as (more commonly) templating the build script
#  itself (using Jinja2). Actual logic provided by plugins in 'plugins/variables/'
#  --------------------------------------------------------------------------

from vespene.common.plugin_loader import PluginLoader

class VariableManager(object):

    def __init__(self, project):
        self.project = project
        self.plugin_loader = PluginLoader()

    def compute(self):
        results = dict()
        variable_plugins = self.plugin_loader.get_variable_plugins()
        for plugin in variable_plugins:
            computed = plugin.compute(self.project, results)
            assert computed is not None
            results.update(computed)
        return results
