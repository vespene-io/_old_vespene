#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  admin.py - sets up the django administrative interface forms at
#  http://yourserver.example.com/admin, which requires superuser access
#  --------------------------------------------------------------------------

from django.contrib import admin

from vespene.models.build import Build
from vespene.models.pipeline import Pipeline
from vespene.models.project import Project
from vespene.models.service_login import ServiceLogin
from vespene.models.snippet import Snippet
from vespene.models.ssh_key import SshKey
from vespene.models.variable_set import VariableSet
from vespene.models.worker import Worker
from vespene.models.worker_pool import WorkerPool
from vespene.models.organization import Organization

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass

@admin.register(SshKey)
class SshKeyAdmin(admin.ModelAdmin):
    pass    

@admin.register(ServiceLogin)
class ServiceLoginAdmin(admin.ModelAdmin):
    pass    

@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    pass    

@admin.register(Worker)
class Worker(admin.ModelAdmin):
    pass

@admin.register(WorkerPool)
class WorkerPoolAdmin(admin.ModelAdmin):
    pass    

@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    pass    

@admin.register(VariableSet)
class VariableSetAdmin(admin.ModelAdmin):
    pass    

@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    pass    

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    pass    

from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

class GroupAdmin(GroupAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'permissions' in form.base_fields:
            permissions = form.base_fields['permissions']
            permissions.queryset = permissions.queryset.none()
        return form

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)