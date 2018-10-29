#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#---------------------------------------------------------------------------
# service_login.py - a username/password combo, most likely for accessing
# a SCM like git when SSH keys are not used.
#---------------------------------------------------------------------------

from django.contrib.auth.models import Group, User
from django.db import models
from vespene.common.secrets import SecretsManager

secrets = SecretsManager()

from vespene.models import BaseModel

class ServiceLogin(models.Model, BaseModel):

    class Meta:
        db_table = 'service_logins'
        indexes = [
            models.Index(fields=['name'], name='service_login_name_idx'),
        ]

    name = models.CharField(unique=True, max_length=512)
    description = models.TextField(blank=True)
    username = models.CharField(max_length=512)
    password = models.CharField(max_length=512, blank=True)
    created_by = models.ForeignKey(User, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    owner_groups = models.ManyToManyField(Group, related_name='service_logins', blank=True)            

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.password = secrets.cloak(self.password)
        super().save(*args, **kwargs)

    def get_password(self):
        return secrets.decloak(self.password)

