#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#---------------------------------------------------------------------------
# ssh_key.py - holds SSH private keys, with optional unlock passwords,
# for use by SCM checkouts or SSH-based management of hosts when running
# the build scripts
#---------------------------------------------------------------------------

from django.contrib.auth.models import Group, User
from django.db import models
from vespene.common.secrets import SecretsManager
from vespene.models import BaseModel
from vespene.common.logger import Logger

LOG = Logger()
secrets = SecretsManager()

class SshKey(models.Model, BaseModel):

    # NOTE: we don't support support SSH with password

    class Meta:
        db_table = 'ssh_keys'
        indexes = [
            models.Index(fields=['name'], name='ssh_key_name_idx'),
        ]

    # TODO: FIXME: encrypt these in database using Django secrets
    name = models.CharField(unique=True, max_length=512)
    description = models.TextField(blank=True)
    private_key = models.TextField(blank=True)
    unlock_password = models.CharField(help_text="provide passphrase only for locked keys", max_length=512, blank=True)
    created_by = models.ForeignKey(User, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    owner_groups = models.ManyToManyField(Group, related_name='ssh_keys',blank=True)

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        self.private_key = secrets.cloak(self.private_key)
        self.unlock_password = secrets.cloak(self.unlock_password)
        super().save(*args, **kwargs)

    def get_private_key(self):
        return secrets.decloak(self.private_key)

    def get_unlock_password(self):
        return secrets.decloak(self.unlock_password)