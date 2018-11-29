#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  permissions.py - central point for all code to use to ask questions about
#  what things are allowed.  Just returns yes/no, does not raise exceptions.
#  Implemented by deferring to plugins in 'plugins/authorization' as configured
#  in settings.
#  --------------------------------------------------------------------------

from vespene.common.logger import Logger
from vespene.common.plugin_loader import PluginLoader

LOG = Logger()

class PermissionsManager(object):

    def __init__(self):
        self.plugin_loader = PluginLoader()
        self.plugins = self.plugin_loader.get_authorization_plugins()

    def _all_true(self, method, subject, request, *args, **kwargs):
        for plugin in self.plugins:
            fn = getattr(plugin, method)
            if not fn(subject, request, *args, **kwargs):
                return False
        return True

    def filter_queryset_for_list(self, qs, request, *args, **kwargs):
        result_qs = qs
        for plugin in self.plugins:
            result_qs = plugin.filter_queryset_for_list(result_qs, request, *args, **kwargs)
        return result_qs

    def filter_queryset_for_view(self, qs, request, *args, **kwargs):
        result_qs = qs
        for plugin in self.plugins:
            result_qs = plugin.filter_queryset_for_view(result_qs, request, *args, **kwargs)
        return result_qs

    def filter_queryset_for_delete(self, qs, request, *args, **kwargs):
        result_qs = qs
        for plugin in self.plugins:
            result_qs = plugin.filter_queryset_for_delete(result_qs, request, *args, **kwargs)
        return result_qs

    def filter_queryset_for_edit(self, qs, request, *args, **kwargs):
        result_qs = qs
        for plugin in self.plugins:
            result_qs = plugin.filter_queryset_for_edit(result_qs, request, *args, **kwargs)
        return result_qs

    def check_can_view(self, obj, request, *args, **kwargs):
        return self._all_true('check_can_view', obj, request, *args, **kwargs)

    def check_can_edit(self, obj, request, *args, **kwargs):
        return self._all_true('check_can_edit', obj, request, *args, **kwargs)

    def check_can_delete(self, obj, request, *args, **kwargs):
        return self._all_true('check_can_delete', obj, request, *args, **kwargs)

    def check_can_create(self, cls, request, *args, **kwargs):
        return self._all_true('check_can_create', cls, request, *args, **kwargs)
    
    def check_can_start(self, obj, request, *args, **kwargs):
        return self._all_true('check_can_start', obj, request, *args, **kwargs)

    def check_can_stop(self, obj, request, *args, **kwargs):
        return self._all_true('check_can_view', obj, request, *args, **kwargs)

