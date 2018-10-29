#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  registration.py - updates the database to say who is building something
#  and what the current settings are, which is used by the file serving
#  code to see if it is ok to serve up files in the buildroot.  But also
#  for record keeping.
#  --------------------------------------------------------------------------


from datetime import datetime
import random
import fcntl
import subprocess
import os

from django.utils import timezone
from django.conf import settings

from vespene.common.logger import Logger
from vespene.models.worker import Worker

LOG = Logger()

WORKER_ID_FILE = "/etc/vespene/worker_id"

# =============================================================================

class RegistrationManager(object):

    def __init__(self, builder, build):
        self.builder = builder
        self.build = build
        self.project = self.build.project
       
    def create_worker_id(self):
        wid = ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))
        fd = open(WORKER_ID_FILE, "w+")
        fd.write(wid)
        fd.close()
        return wid

    def get_worker_id(self, fd):
        return fd.readlines()[0].strip()

    def get_worker_record(self, worker_id):
        qs = Worker.objects.filter(worker_uid=worker_id)
        if not qs.exists():
            return None
        return qs.first()

    # worker_pool = models.ForeignKey('WorkerPool', null=False, on_delete=models.SET_NULL)
    # hostname = models.CharField(max_length=1024, null=True)
    # port = models.IntField(null=False, default=8080)
    # working_dir = models.CharField(max_length=1024, null=True)
    # first_checkin = models.DateTimeField(null=True, blank=True)
    # last_checkin = models.DateTimeField(null=True, blank=True)
    # fileserving_enabled = models.BooleanField(null=False, default=False)

    def get_hostname(self):
        if settings.FILESERVING_HOSTNAME:
            return settings.FILESERVING_HOSTNAME
        return self.guess_hostname()

    def guess_hostname(self):
        return subprocess.check_output("hostname").decode('utf-8').strip()

    def get_port(self):
        if settings.FILESERVING_PORT:
            return settings.FILESERVING_PORT
        else:
            return 8000

    def get_build_root(self):
        return settings.BUILD_ROOT

    def get_fileserving_enabled(self):
        return settings.FILESERVING_ENABLED

    def create_worker_record(self, worker_id):
        now = datetime.now(tz=timezone.utc)
        obj = Worker(
            worker_uid = worker_id,
            hostname = self.get_hostname(),
            port = self.get_port(),
            build_root = self.get_build_root(),
            first_checkin = now,
            last_checkin = now,
            fileserving_enabled = self.get_fileserving_enabled()
        )
        obj.save()
        return obj

    def update_worker_record(self, worker):
        now = datetime.now(tz=timezone.utc)
        worker.hostname = self.get_hostname()
        worker.port = self.get_port()
        worker.build_root = self.get_build_root()
        worker.last_checkin = now
        worker.fileserving_enabled = self.get_fileserving_enabled()
        worker.save()
        return worker

    def go(self):
        """
        Trigger next stage of pipeline if build was successful
        """

        if not os.path.exists(WORKER_ID_FILE):
            worker_id = self.create_worker_id()
        
        fd = open(WORKER_ID_FILE, "r")
        fcntl.flock(fd, fcntl.LOCK_EX)
        worker_id = self.get_worker_id(fd)

        worker_record = self.get_worker_record(worker_id)
        if not worker_record:
            worker_record = self.create_worker_record(worker_id)
        else:
            worker_record = self.update_worker_record(worker_record)

        self.build.worker = worker_record
        self.build.save()
        fcntl.flock(fd, fcntl.LOCK_UN)
