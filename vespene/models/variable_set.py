#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#---------------------------------------------------------------------------
# variable_set.py - a bucket of reusable variables that may be attached
# to multiple objects, all sharing the same keys and values.
#---------------------------------------------------------------------------

from django.contrib.auth.models import Group, User
from django.db import models

from vespene.models import BaseModel


class VariableSet(models.Model, BaseModel):

    class Meta:
        db_table = 'variable_sets'

    name = models.CharField(unique=True, max_length=512)
    description = models.TextField(blank=True)
    variables = models.TextField(help_text="JSON", blank=True, null=False, default="{}")

    created_by = models.ForeignKey(User, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    owner_groups = models.ManyToManyField(Group, related_name='variable_sets', blank=True)

    def __str__(self):
        return self.name
