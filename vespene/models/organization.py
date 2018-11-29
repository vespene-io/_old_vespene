#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#---------------------------------------------------------------------------
# organization.py - a model of an organization like GitHub organizations
# holding lots of repos for import
#---------------------------------------------------------------------------

import json

from django.contrib.auth.models import Group, User
from django.db import models

from vespene.manager import Shared
from vespene.common.logger import Logger
from vespene.models import BaseModel, as_dict
from vespene.models.build import QUEUED, RUNNING, UNKNOWN
from vespene.manager.permissions import PermissionsManager

permissions = PermissionsManager()
LOG = Logger()

class Organization(models.Model, BaseModel):
    class Meta:
        db_table = 'organizations'
        indexes = [
            models.Index(fields=['name'], name='organization_name_idx'),
        ]

    name = models.CharField(unique=True, max_length=512)
    description = models.TextField(blank=True)

    organization_type = models.CharField(max_length=100)
    organization_identifier = models.CharField(max_length=512, help_text="example: 'vespene-io' for github.com/vespene-io/")
    api_endpoint = models.CharField(max_length=512, blank=True, default="", help_text="blank, or https://{hostname}/api/v3 for GitHub Enterprise")

    import_enabled = models.BooleanField(default=True)

    import_without_dotfile = models.BooleanField(default=False)
    overwrite_project_name = models.BooleanField(default=True)
    overwrite_project_script = models.BooleanField(default=True)
    overwrite_configurations = models.BooleanField(default=True)
    allow_pipeline_definition = models.BooleanField(default=True)
    allow_worker_pool_assignment = models.BooleanField(default=True)
    auto_attach_ssh_keys = models.ManyToManyField('SshKey', related_name='+', blank=True, help_text="SSH keys to be assigned to imported projects")
    default_worker_pool = models.ForeignKey('WorkerPool', related_name='+', null=False, on_delete=models.PROTECT)

    force_rescan = models.BooleanField(default=False, help_text="rescan once at the next opportunity, ignoring refresh_minutes")
    refresh_minutes = models.IntegerField(default=120)
    scm_login = models.ForeignKey('ServiceLogin', related_name='organizations', on_delete=models.SET_NULL, null=True, help_text="... or add an SSH key in the next tab", blank=True)

    worker_pool = models.ForeignKey('WorkerPool', related_name='organizations', null=False, on_delete=models.PROTECT)
    
    created_by = models.ForeignKey(User, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)

    last_build = models.ForeignKey('Build', null=True, blank=True, related_name='last_build_for_organization', on_delete=models.SET_NULL)
    active_build = models.ForeignKey('Build', null=True, blank=True, related_name='active_build_for_organization', on_delete=models.SET_NULL)
    last_successful_build = models.ForeignKey('Build', null=True, blank=True, related_name='last_successful_build_for_organization', on_delete=models.SET_NULL)

    def __str__(self):
        return self.name    

       
