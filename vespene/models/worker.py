#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  ---------------------------------------------------------------------------
#  worker.py - represents a worker registering current settings and location
#  when it starts up.
#  --------------------------------------------------------------------------

from django.db import models
from vespene.models import BaseModel

class Worker(models.Model, BaseModel):

    class Meta:
        db_table = 'workers'
        indexes = [
            models.Index(fields=['worker_uid'], name='worker_uid_idx'),
        ]

    worker_uid = models.CharField(unique=True, max_length=512)
    hostname = models.CharField(max_length=1024, null=True)
    port = models.IntegerField(null=False, default=8080)
    build_root = models.CharField(max_length=1024, null=True)
    first_checkin = models.DateTimeField(null=True, blank=True)
    last_checkin = models.DateTimeField(null=True, blank=True)
    fileserving_enabled = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.hostname
