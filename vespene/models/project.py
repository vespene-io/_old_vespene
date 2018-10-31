#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#---------------------------------------------------------------------------
# project.py - model & behavior for projects, which involve a build
# script and sometimes a source code repo.  Instances of projects
# building are ... builds.  See build.py
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

DEFAULT_SCRIPT = """#!/bin/bash
echo "replace this section"
"""

class Project(models.Model, BaseModel):
    class Meta:
        db_table = 'projects'
        indexes = [
            models.Index(fields=['name'], name='project_name_idx'),
        ]

    name = models.CharField(unique=True, max_length=512)
    pipeline = models.ForeignKey('Pipeline', blank=True, null=True, max_length=512, related_name='projects', on_delete=models.SET_NULL)
    pipeline_enabled = models.BooleanField(default=True)

    stage = models.ForeignKey('Stage', null=True, blank=True, related_name='projects', on_delete=models.SET_NULL)

    last_build = models.ForeignKey('Build', null=True, blank=True, related_name='last_build_for_project', on_delete=models.SET_NULL)
    active_build = models.ForeignKey('Build', null=True, blank=True, related_name='active_build_for_project', on_delete=models.SET_NULL)
    last_successful_build = models.ForeignKey('Build', null=True, blank=True, related_name='last_successful_build_for_project', on_delete=models.SET_NULL)
    
    description = models.TextField(blank=True)
    repo_url = models.CharField(max_length=1024, help_text="ex: git@github.com:your_username/your_repo.git", blank=True)
    repo_branch = models.CharField(max_length=255, help_text="default: master", blank=True, null=False, default="")

    scm_type = models.CharField(null=False, max_length=30)
    webhook_enabled = models.BooleanField(default=False)
    webhook_token = models.CharField(default="", max_length=128, blank=True, null=True, help_text="an optional project-specific query string to require")
    script = models.TextField(help_text="Interpreter line is required. Exit 0 for success. {{jinja2}} is allowed.", default=DEFAULT_SCRIPT, null=True)
    timeout = models.IntegerField(help_text="Fail the build automatically after this many minutes", default=60, blank=False, null=False)
    container_base_image = models.CharField(max_length=512, blank=True, null=True, help_text="only for container isolated builds")

    variables = models.TextField(null=True, help_text="JSON {}", default="{}")
    variable_sets = models.ManyToManyField('VariableSet', related_name='projects', blank=True)
    launch_questions = models.TextField(null=False, default="[]", help_text="JSON. See project docs for spec.")

    scm_login = models.ForeignKey('ServiceLogin', related_name='projects', on_delete=models.SET_NULL, null=True, help_text="... or add an SSH key in the SSH tab", blank=True)
    ssh_keys = models.ManyToManyField('SshKey', related_name='projects', blank=True, help_text="ssh-add these keys before the checkout starts")

    worker_pool = models.ForeignKey('WorkerPool', related_name='projects', null=False, on_delete=models.PROTECT, help_text="where should this build be run?")

    created_by = models.ForeignKey(User, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    owner_groups = models.ManyToManyField(Group, related_name='projects', blank=True)
    launch_groups = models.ManyToManyField(Group, related_name='can_launch_projects', blank=True, help_text="these groups can launch builds of this project")

    # scheduling
    schedule_enabled = models.BooleanField(default=False)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    weekday_start_hours = models.CharField(max_length=512, blank=True, null=True, default="", help_text="24 hour UTC specifier, Ex: '0,8,16' OR '3' OR '0-24'")
    weekday_start_minutes = models.CharField(max_length=512, blank=True, null=True, default="", help_text="Ex: 0, 30")
    weekend_start_hours = models.CharField(max_length=512, blank=True, null=True, default="", help_text="24 hour UTC specifier, Ex: '0,8,16' OR '3' OR '0-24'")
    weekend_start_minutes = models.CharField(max_length=512, blank=True, null=True, default="", help_text="Ex: 0, 30")
    schedule_threshold = models.IntegerField(default=10, blank=True, null=False, help_text="do not queue a build if one was already queued up this many minutes ago")

    def __str__(self):
        return self.name    

    def is_active(self):
        return self.active_build and self.active_build.is_active()

    def has_launch_questions(self):
        return self.launch_questions is not None and self.launch_questions != "[]"

    def get_launch_questions(self):
        if not self.has_launch_questions():
            return []
        try:
            return json.loads(self.launch_questions)
        except:
            return -1

    def explain_status(self):
        build = self.last_build
        if build is None:
            return UNKNOWN
        return build.explain_status()

    def as_dict(self):
        # rough serialization used by the backend, not REST API
        return dict(
            id = self.id,
            name = self.name,
            last_build = as_dict(self.last_build),
            active_build = as_dict(self.active_build),
            last_successful_build = as_dict(self.last_successful_build),
            description = self.description,
            repo_url = self.repo_url,
            script = self.script,
            variables = self.variables,
            worker_pool = as_dict(self.worker_pool)
        )

    def is_startable(self):
        if self.active_build is None:
            return True
        elif self.active_build.status in [ RUNNING, QUEUED ]:
            return False
        # this final state should really not occur
        else:
            return True

    def start(self, pipeline_parent_build=None):
        from vespene.manager import jobkick
        LOG.info("starting project: %s" % self)
        jobkick.start_project(self, pipeline_parent_build=pipeline_parent_build)

    def stop(self):
        from vespene.manager import jobkick
        LOG.info("stopping project: %s" % self)
        jobkick.stop_project(self)

       
