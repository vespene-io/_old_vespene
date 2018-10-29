#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  group_required.py - a plugin to limit access to certain types of
#  verbs on certain types of nouns to certain groups. See web 'authz'
#  documentation for more info.  DO NOT USE THIS PLUGIN without
#  also enabling the 'ownership' plugin, or the default security
#  rules will not work as expected.
#  --------------------------------------------------------------------------

from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from vespene.common.logger import Logger
from vespene.manager import Shared

LOG = Logger()

class Plugin(object):

    def __init__(self, parameters):
        self.cfg = parameters

    def required_groups(self, cls, verb):
        name = cls.__name__.split('.')[-1].lower()
        class_cfg = self.cfg.get(name, {})
        verb_cfg = class_cfg.get(verb, None)
        return verb_cfg

    def matches(self, cls, verb, request):
        if request.user.is_superuser:
            return True
        groups = self.required_groups(cls, verb)
        if groups is None:
            return True
        required = set(self.required_groups(cls, verb))
        groups = set([ g.name for g in request.user.groups.all() ])
        both = required.intersection(groups)
        return len(both) > 0

    def check_can_list(self, cls, request, *args, **kwargs):
        return self.matches(cls, 'list', request)

    def check_can_create(self, cls, request, *args, **kwargs):
        return self.matches(cls, 'create', request)

    def filter_queryset_for_list(self, queryset, request, *args, **kwargs):
        return queryset

    def filter_queryset_for_view(self, queryset, request, *args, **kwargs):
        return queryset
        
    def filter_queryset_for_edit(self, queryset, request, *args, **kwargs):
        return queryset
     
    def filter_queryset_for_delete(self, queryset, request, *args, **kwargs):
        return queryset

    def check_can_view(self, obj, request, *args, **kwargs):
        return self.matches(obj.__class__, 'view', request)

    def check_can_edit(self, obj, request, *args, **kwargs):
        return self.matches(obj.__class__, 'edit', request)

    def check_can_delete(self, obj, request, *args, **kwargs):
        return self.matches(obj.__class__, 'delete', request)

    def check_can_start(self, obj, request, *args, **kwargs):
        rc = self.matches(obj.__class__, 'start', request)
        return rc

    def check_can_stop(self, obj, request, *args, **kwargs):
        return self.matches(obj.__class__, 'stop', request)


