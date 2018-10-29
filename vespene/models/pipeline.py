#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#---------------------------------------------------------------------------
# pipeline.py - model/behavior code for CI/CD pipelines
#---------------------------------------------------------------------------

from django.contrib.auth.models import Group, User
from django.db import models

from vespene.common.logger import Logger
from vespene.models import BaseModel
from vespene.models.project import Project
from vespene.models.stage import Stage

LOG = Logger()

class Pipeline(models.Model, BaseModel):

    """
    First create tags, such as "build", "qa", "stage", "integration" and deploy"
    Tag each project build step as appropriate
    """

    class Meta:
        db_table = 'pipelines'
        indexes = [
            models.Index(fields=['name'], name='pipeline_name_idx'),
            models.Index(fields=['group_name'], name='pipeline_group_name_idx'),
        ]

    name = models.CharField(unique=True, max_length=512)
    description = models.TextField(blank=True)

    enabled = models.BooleanField(default=True)
    group_name = models.CharField(blank=False, null=False, max_length=512)
    last_completed_date = models.DateTimeField(null=True, blank=True)
    last_completed_by = models.ForeignKey('Build', related_name='completes_pipeline', on_delete=models.SET_NULL, null=True, blank=True)

    variables = models.TextField(blank=True, null=False, default="{}")
    variable_sets = models.ManyToManyField('VariableSet', related_name='pipelines', blank=True)

    stage1 = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    stage2 = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    stage3 = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='+',  blank=True, null=True)
    stage4 = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    stage5 = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    stage6 = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    stage7 = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
  
    created_by = models.ForeignKey(User, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    owner_groups = models.ManyToManyField(Group, related_name='pipelines', blank=True)

    def all_stages(self):
        return [ x for x in [ self.stage1, self.stage2, self.stage3, self.stage4, self.stage5, self.stage6, self.stage7 ] if x is not None ]

    def all_projects(self):
        stage_ids = [ s.id for s in self.all_stages() ]
        return Project.objects.filter(pipeline=self, stage__pk__in=stage_ids)

    def __str__(self):
        return self.name    

    def start(self):
        LOG.info("starting pipeline: %s" % self)
        if self.stage1 is None:
            raise Exception("stage1 is not configured")
        self.start_stage(self.stage1)

    def start_stage(self, stage):
        LOG.info("starting stage: %s" % stage)
        if not self.enabled:
            raise Exception("pipeline is disabled")
        projects = Project.objects.filter(stage = stage, pipeline = self).all()
        for p in projects:
            if p.is_startable() and p.pipeline_enabled:
                p.start()
            elif not p.pipeline_enabled:
                LOG.info("project is disabled in pipeline: %s" % p)
            else:
                LOG.info("project does not need to be started: %s" % p)

    def next_stage(self, current_stage):
        if self.stage1 is not None and (self.stage1.pk == current_stage.pk):
            return self.stage2
        elif self.stage2 is not None and (self.stage2.pk == current_stage.pk):
            return self.stage3
        elif self.stage3 is not None and (self.stage3.pk == current_stage.pk):
            return self.stage4
        elif self.stage4 is not None and (self.stage4.pk == current_stage.pk):
            return self.stage5
        elif self.stage5 is not None and (self.stage5.pk == current_stage.pk):
            return self.stage6
        elif self.stage6 is not None and (self.stage6.pk == current_stage.pk):
            return self.stage7
        return None

    def previous_stage(self, current_stage):
        if self.stage1 is not None and (self.stage1.pk == current_stage.pk):
            return None
        elif self.stage2 is not None and (self.stage2.pk == current_stage.pk):
            return self.stage1
        elif self.stage3 is not None and (self.stage3.pk == current_stage.pk):
            return self.stage2
        elif self.stage4 is not None and (self.stage4.pk == current_stage.pk):
            return self.stage3
        elif self.stage5 is not None and (self.stage5.pk == current_stage.pk):
            return self.stage4
        elif self.stage6 is not None and (self.stage6.pk == current_stage.pk):
            return self.stage5
        elif self.stage7 is not None and (self.stage7.pk == current_stage.pk):
            return self.stage6
        return None

    def all_previous_stages(self, current_stage):
        results = []
        ptr = current_stage
        while True:
            previous = self.previous_stage(ptr)
            if previous is None:
                return results
            results.append(previous)
            ptr = previous
