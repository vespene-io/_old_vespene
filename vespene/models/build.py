#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  --------------------------------------------------------------------------
#  build.py - a build is an execution of a project, involving optionally
#  a checkout, and a definite execution of a templated build script. It has
#  status. A build object represents both a request to build, and the status
#  of an in-progress or completed build.
#  --------------------------------------------------------------------------

import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from vespene.models import BaseModel

FAILURE = "FAILURE"
BLOCKED = "BLOCKED"
SUCCESS = "SUCCESS"
ABORTED = "ABORTED"
RUNNING = "RUNNING"
QUEUED = "QUEUED"
ORPHANED = "ORPHANED"
ABORTING = "ABORTING"
UNKNOWN = "UNKNOWN"

BUILD_STATUS_CHOICES = (
    (RUNNING, 'Running'),
    (FAILURE, 'Failure'),
    (SUCCESS, 'Success'),
    (ABORTED, 'Aborted'),
    (ABORTING, 'Aborting'),
    (ORPHANED, 'Orphaned'),
    (QUEUED, 'Queued')
)

output_manager = None

class Build(models.Model, BaseModel):

    class Meta:
        db_table = 'builds'
        indexes = [
            models.Index(fields=['project'], name='execution_project_idx'),
        ]

    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, null=True)

    # internal builds are not initiated through jobkick, user timer, or webhook but are artifacts produced by internal operations
    # they include things like GitHub organizational scans
    is_internal = models.BooleanField(default=False, blank=True)

    pipeline = models.ForeignKey('Project', on_delete=models.SET_NULL, related_name='builds', null=True, blank=True)
    revision = models.CharField(null=True, blank=True, max_length=20)
    revision_username = models.CharField(null=True, blank=True, max_length=512)
    queued_time = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    return_code = models.IntegerField(null=True, blank=True)

    status = models.CharField(default=UNKNOWN, choices=BUILD_STATUS_CHOICES, max_length=20, null=False)
    worker_pool = models.ForeignKey('WorkerPool', related_name='builds', null=False, on_delete=models.CASCADE)

    output = models.TextField(null=True, blank=True)
    messages = models.TextField(null=True, blank=True)

    working_dir = models.CharField(blank=True, max_length=1024)
    variables = models.TextField(null=False, default="{}")
    launch_answers = models.TextField(null=True, default="{}")
    output_variables = models.TextField(null=False, default="{}", help_text="JSON. See project docs for spec.")

    script = models.TextField(null=True, blank=True)

    created_by = models.ForeignKey(User, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    pipeline_origin_build_id = models.IntegerField(null=True, blank=True)
    pipeline_parent_build_id = models.IntegerField(null=True, blank=True)
    worker = models.ForeignKey('Worker', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.pk)

    def is_active(self):
        return self.status == RUNNING

    def is_complete(self):
        return not self.is_active() and not self.status == QUEUED

    def is_stoppable(self):
        return self.status in [ RUNNING, QUEUED ]

    def explain_status(self):
        return self.status.title()

    def stop(self):
        import jobkick
        jobkick.stop_build(self)

    def restart(self):
        import jobkick
        jobkick.start_build(self)

    def as_dict(self):
        # rough serialization used by the backend, not REST API
        return dict(
            id = self.id,
            revision = self.revision,
            start_time = str(self.start_time),
            end_time = str(self.end_time),
            status = self.status,
            working_dir = self.working_dir,
            variables = self.variables
        )

    def duration(self):
        """
        provides a calculated duration even while the build is running, which is why it is not a DB value
        """
        if self.start_time is None:
            return None
        end_time = self.end_time
        if end_time is None:
            if self.status in [ RUNNING ]:
                end_time = datetime.datetime.now(tz=timezone.utc)
            else:
                return None
        return end_time - self.start_time

    def get_output(self):
        global output_manager
        from vespene.manager.output import OutputManager
        if output_manager is None:
            output_manager = OutputManager()
        return output_manager

    def append_output(self, output):
        """
        Append 'output' to the build log.
        """
        # TODO: is there a more efficient DB-way to do this?
        output = self.get_output().get_msg(self, output)
        if self.output is None:
            self.output = ""
        if output:
            self.output = self.output + output
            self.save(force_update=True)

    def append_message(self, output):
        output = self.get_output().get_msg(self, output)
        if self.messages is None:
            self.messages = ""
        if output:
            # TODO: only join this (and above function) with extra "\n" if needed.
            self.messages = self.messages + "\n" + output
            self.save(force_update=True)

