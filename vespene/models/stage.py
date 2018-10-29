#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#---------------------------------------------------------------------------
# stage.py - one of many steps of a CI/CD pipeline. See pipelines.py
#---------------------------------------------------------------------------

from django.db import models

from vespene.models import BaseModel

class Stage(models.Model, BaseModel):

    class Meta:
        db_table = 'stage'
        indexes = [
            models.Index(fields=['name'], name='stage_name_idx')
        ]

    name = models.CharField(unique=True, max_length=512)
    description = models.TextField(blank=True)

    variables = models.TextField(null=False, help_text="JSON", default="{}", blank=True)
    variable_sets = models.ManyToManyField('VariableSet', related_name='stages', blank=True)

    def __str__(self):
        return self.name
