#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  plugin_loader.py - generic mechanism to load plugins used by all
#  types of plugins in Vespene. Some plugins return lists, others
#  return dictionaries, it depends on whether they are typically accessed
#  by name or just wrap lots of behaviors which stack additively.
#  --------------------------------------------------------------------------

from importlib import import_module

from django.conf import settings

# in the future not all plugin definitions may required and a partially empty plugins 
# list may be ok to enable smooth upgrades. this is the list of required plugins at 
# first release ONLY, and some of these plugins, without a definition, mean Vespene
# has no core behavior.

REQUIRED_PLUGIN_KEYS = ( 'pre_triggers', 'success_triggers', 'failure_triggers', 'isolation', 'authorization', 'scm', 'variables', 'output', 'secrets', 'organizations' )

class PluginLoader(object):

    def __init__(self):
        self.conf = settings.PLUGIN_CONFIGURATION
        self.check_plugin_configuration()

    def check_plugin_configuration(self):
        for x in REQUIRED_PLUGIN_KEYS:
            if x not in self.conf:
                raise Exception("missing %s configuration in plugin configuration" % x)

    def get_module_instance(self, name, arguments=None):
        imported_module = import_module(name) # package='vespene')
        cls = getattr(imported_module, 'Plugin')
        if arguments:
            return cls(arguments)
        else:
            return cls()

    def generic_load(self, section, as_list=False, just_names=False):
        results = dict()
        for (k, v) in self.conf[section].items():
            if not just_names:
                if type(v) == list:
                    results[k] = self.get_module_instance(v[0], v[1])
                else:
                    results[k] = self.get_module_instance(v)
            else:
                results[k] = k
        if as_list or just_names:
            return [ x for x in results.values() ]
        else:
            return results

    def get_pre_trigger_plugins(self):
        return self.generic_load('pre_triggers', as_list=True)

    def get_success_trigger_plugins(self):
        return self.generic_load('success_triggers', as_list=True)

    def get_failure_trigger_plugins(self):
        return self.generic_load('failure_triggers', as_list=True)

    def get_scm_plugins(self):
        return self.generic_load('scm')

    def get_isolation_plugins(self):
        return self.generic_load('isolation')

    def get_variable_plugins(self):
        return self.generic_load('variables', as_list=True)

    def get_authorization_plugins(self):
        return self.generic_load('authorization', as_list=True)

    def get_secrets_plugins(self):
        return self.generic_load('secrets', as_list=True)

    def get_output_plugins(self):
        return self.generic_load('output', as_list=True)

    def get_isolation_choices(self):
        return [ (x, x) for x in self.generic_load('isolation', just_names=True) ]

    def get_scm_choices(self):
        return [ (x, x) for x in self.generic_load('scm', just_names=True) ]

    def get_organization_plugins(self):
        return self.generic_load('organizations')        