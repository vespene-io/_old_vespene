#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  ownership.py - this implements an AuthZ structure that allows users
#  to create mostly everything, but only edit/delete objects that they
#  have created, or been marked as an owner of.
#  --------------------------------------------------------------------------

from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from vespene.common.logger import Logger
from vespene.manager import Shared

LOG = Logger()

# This is a particularly involved authentication ownership filter that has the following behavior:
# 
# - Admins can do everything
# - Users can edit objects they are owners of and delete objects they are owners of
# - Projects, Pipelines, and Builds can be launched if ownership is available of those items
#  but ownership of the SSH Keys and Service Logins assigned is not required.
#  Build ownership looks to the project.

class Plugin(object):

    def __init__(self, parameters=None):
        self.parameters = parameters
        if parameters is None:
            self.parameters = {}
        self.filter_view = self.parameters.get('filter_view', False)

    def check_can_list(self, cls, request, *args, **kwargs):
        # anybody can list any type of object
        if request.user.is_superuser:
            return True
        # note that for a Project class we must return True or the index will infinite loop from login
        # until the index page is *NOT* the same as the project list.
        # instead use filter_queryset to limit what projects are shown for now.
        return True

    def check_can_create(self, cls, request, *args, **kwargs):

        # Vespene installs that do not want all users to be able to make new objects (like projects) should write a *second* plugin
        # and load it after ownership in settings. Right now, all users can create projects.

        from vespene.models.worker_pool import WorkerPool
        from vespene.models.build import Build
        from django.contrib.auth.models import User, Group

        if cls in [ Build ]:
            return False

        # superusers can make everything
        if request.user.is_superuser:
            return True
        if cls in [ WorkerPool, User, Group ]:
            return False
        return True

    def _ownership_filter(self, queryset, request, *args, **kwargs):

        from vespene.models.build import Build
        from django.contrib.auth.models import User, Group
        from vespene.models.variable_set import VariableSet
        from vespene.models.pipeline import Pipeline
        from vespene.models.snippet import Snippet
        from vespene.models.stage import Stage
        from vespene.models.project import Project
        from vespene.models.worker_pool import WorkerPool
        from vespene.models.organization import Organization

        for_view = kwargs.get('for_view', False)

        if for_view and queryset.model in [ VariableSet, Group, Snippet, Pipeline, Stage, WorkerPool, Organization ]:
            return queryset
        if request.user.is_superuser:
            return queryset
        if request.user.is_anonymous:
            return queryset.none()
        group_ids = [ x.pk for x in request.user.groups.all() ]
        if queryset.model == User:
            queryset = queryset.filter(pk = request.user.pk)
        elif queryset.model == Group:
            queryset = queryset.none()
        elif queryset.model == Build:
            queryset = queryset.filter(
                Q(created_by=request.user) | Q(project__owner_groups__pk__in=group_ids) 
            ).distinct()
        elif for_view and queryset.model == Project:
            queryset = queryset.filter(
                Q(created_by=request.user) | Q(owner_groups__pk__in=group_ids) | Q(launch_groups__pk__in=group_ids)
            ).distinct()
        else:
            queryset = queryset.filter(
                Q(created_by=request.user) | Q(owner_groups__pk__in=group_ids) 
            ).distinct()
            
        return queryset

    def filter_queryset_for_list(self, queryset, request, *args, **kwargs):

        from django.contrib.auth.models import User, Group
        from vespene.models.build import Build
        from vespene.models.project import Project
        from vespene.models.snippet import Snippet
        from vespene.models.stage import Stage
        from vespene.models.variable_set import VariableSet
        from vespene.models.worker_pool import WorkerPool
        from vespene.models.pipeline import Pipeline
        from vespene.models.organization import Organization

        if request.user.is_anonymous:
            return queryset.none()
        if request.user.is_superuser:
            return queryset

        if self.filter_view:
            return self._ownership_filter(queryset, request, for_view=True)

        return queryset


    def filter_queryset_for_view(self, queryset, request, *args, **kwargs):
        return self.filter_queryset_for_list(queryset, request)
        
    def filter_queryset_for_edit(self, queryset, request, *args, **kwargs):

        from vespene.models.build import Build
        from vespene.models.stage import Stage
        from vespene.models.worker_pool import WorkerPool
        from vespene.models.organization import Organization

        if queryset.model == Build:
            # because these are never user editable
            return queryset.none()
        if request.user.is_anonymous:
            return queryset.none()
        if request.user.is_superuser:
            return queryset
        if queryset.model in [ WorkerPool, Stage, Organization ]:
            return queryset.none()
        return self._ownership_filter(queryset, request, *args, **kwargs)  

    def filter_queryset_for_delete(self, queryset, request, *args, **kwargs):
        return self.filter_queryset_for_edit(queryset, request, *args, **kwargs)

    def check_can_view(self, obj, request, *args, **kwargs):
        viewable = self.filter_queryset_for_view(obj.__class__.objects, request, *args, **kwargs)
        return viewable.filter(pk=obj.pk).exists()

    def check_can_edit(self, obj, request, *args, **kwargs):
        editable = self.filter_queryset_for_edit(obj.__class__.objects, request, *args, **kwargs)
        result = editable.filter(pk=obj.pk).exists()
        return result

    def check_can_delete(self, obj, request, *args, **kwargs):
        deleteable = self.filter_queryset_for_delete(obj.__class__.objects, request, *args, **kwargs)
        return deleteable.filter(pk=obj.pk).exists()

    def _has_ownership(self, request, obj):
        # does the request.user have ownership of the object?
        qs = obj.__class__.objects.filter(pk=obj.pk)
        if not qs.exists():
            return False
        return self._ownership_filter(qs, request).exists()

    def is_in_launch_groups(self, obj, request):
        from vespene.models.build import Build
        group_ids = [ x.pk for x in request.user.groups.all() ]
        if type(obj) != Build:
            return obj.__class__.objects.filter(pk=obj.pk, launch_groups__pk__in=group_ids).exists()
        else:
            return obj.__class__.objects.filter(pk=obj.pk, project__launch_groups__pk__in=group_ids).exists()

    def check_can_start(self, obj, request, *args, **kwargs):
        # this requires ability to edit the project to start it, or the
        # user can be in the launch groups
        if self.check_can_edit(obj, request, *args,  **kwargs):
            return True
        else:
            return self.is_in_launch_groups(obj, request)

    def check_can_stop(self, obj, request, *args, **kwargs):
        # same comment as above.
        if self.check_can_edit(obj, request, *args, **kwargs):
            return True
        else:
            return self.is_in_launch_groups(obj, request)

    def matching_groups(self, obj, user):
        groups = set(obj.owner_groups.values_list('id', flat=True))
        my_groups = set(user.groups.values_list('id', flat=True))
        return len(groups.intersection(my_groups)) > 0


