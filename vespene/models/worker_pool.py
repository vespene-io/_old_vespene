#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  ---------------------------------------------------------------------------
#  worker_pool.py - worker pools are named queues with various proprerties.
#  each project has one and only one worker pool and individual workers
#  farm the queue to build jobs assigned to those queues.  More than one
#  worker can farm each queue, but a worker pool without any workers is
#  non-functional.
#  --------------------------------------------------------------------------

from django.contrib.auth.models import User
from django.db import models

from vespene.common.secrets import SecretsManager
from vespene.models import BaseModel

secrets = SecretsManager()

class WorkerPool(models.Model, BaseModel):

    class Meta:
        db_table = 'worker_pools'
        indexes = [
            models.Index(fields=['name'], name='worker_pool_name_idx'),
        ]

    name = models.CharField(unique=True, max_length=512)
    variables = models.TextField(blank=True, null=True, default="{}")
    variable_sets = models.ManyToManyField('VariableSet', related_name='worker_pools', blank=True)

    isolation_method = models.CharField(blank=False, max_length=50)
    sudo_user = models.CharField(max_length=100, blank=True, null=True)
    # FIXME: SECURITY: use the secrets manager code on this as well.
    sudo_password = models.CharField(max_length=100, blank=True, null=True)
    permissions_hex = models.CharField(max_length=5, default="0x777", null=False, blank=False, help_text="permissions for build directory")

    sleep_seconds = models.IntegerField(default=10, blank=False, null=False, help_text="how often workers should scan for builds")
    auto_abort_minutes = models.IntegerField(default=24*60, blank=False, null=False, help_text="auto-abort queued builds after this amount of time in queue")
    build_latest = models.BooleanField(default=True, null=False, help_text="auto-abort duplicate older builds?")
    build_object_shelf_life = models.IntegerField(default=365, blank=False, null=False, help_text="retain build objects for this many days")
    build_root_shelf_life = models.IntegerField(default=31, blank=False, null=False, help_text="retain build roots for this many days")
      
    created_by = models.ForeignKey(User, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.sudo_password = secrets.cloak(self.sudo_password)
        super().save(*args, **kwargs)

    def get_sudo_password(self):
        return secrets.decloak(self.sudo_password)

    def as_dict(self):
        return dict(
            id = self.id,
            name = self.name,
            variables = self.variables,
            isolation_method = self.isolation_method,
            sudo_user = self.sudo_user
        )
