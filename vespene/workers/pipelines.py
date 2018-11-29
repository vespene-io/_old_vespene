#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  pipelines.py - pipelines are the logic Vespene uses to implement
#  a "CI/CD" pipeline where one build can trigger another on success.
#  this is described largely in the web documentation, and flags
#  each project for start using code in 'models/project.py'. A different
#  worker might serve the project when it runs, it is just flagged
#  for starting, not actually kicked off here.
#  --------------------------------------------------------------------------


import datetime

from django.utils import timezone

from vespene.common.logger import Logger
from vespene.models.build import BLOCKED, RUNNING, SUCCESS
from vespene.models.project import Project

LOG = Logger()

# =============================================================================

class PipelineManager(object):

    def __init__(self, builder, build):
        self.builder = builder
        self.build = build
        self.project = self.build.project
       
    def complete_pipeline(self):
        self.project.pipeline.last_completed_date = datetime.datetime.now(tz=timezone.utc)
        self.project.pipeline.last_completed_by = self.build
        self.project.pipeline.save()

    def go(self):
        """
        Trigger next stage of pipeline if build was successful
        """

        # ----------------------------------------------------------------------
        # Are we ready to run the pipeline? Return if not
        
        self.build.append_message("----------\nPipeline evaluation....")

        if self.project.pipeline is None:
            self.build.append_message("no pipeline is configured")
            return

        if self.project.stage is None:
            self.build.append_message("no stage is configured")
            return

        if not self.project.pipeline_enabled:
            self.build.append_message("pipeline is disabled at project level")
            return
        
        if not self.project.pipeline.enabled:
            self.build.append_message("the pipeline is disabled")
            return

        self.build.append_message("processing pipeline: %s" % self.project.pipeline.name)
        self.build.append_message("current stage: %s" % self.project.stage.name)

        # ----------------------------------------------------------------------
        # Are all peer projects done and complete?

        peers = Project.objects.filter(
            pipeline = self.project.pipeline,
            stage = self.project.stage
        ).exclude(
            id = self.project.id
        )

        names = ",".join([ p.name for p in peers.all() ])
        self.build.append_message("peer projects for stage: %s" % names)
        
        blocked = True
        blockers1 = peers.filter(last_build=None)
        blockers2 = peers.exclude(last_build__status=SUCCESS)
        blockers3 = peers.exclude(active_build=None)
 

        if blockers1.count():
            names = ",".join([ b.name for b in blockers1.all() ])
            self.build.append_message("pipeline waiting: need for some projects to build before contining: %s" % names)
        elif blockers2.count():
            names = ",".join([ b.name for b in blockers2.all() ])
            self.build.append_message("pipeline waiting: need for some peer project builds to have a successful status before continuing: %s" % names)
        elif blockers3.count():
            names = ",".join([ b.name for b in blockers3.all() ])
            self.build.append_message("pipeline waiting: need for some peer project builds to complete before continuing: %s" % names)
        else:
            blocked = False

        if blocked: 
            return

        # -----------------------------------------------------------------------
        # What is the next stage of the pipeline?

        current_stage = self.project.stage
        next_stage = None

        pipeline = self.project.pipeline

        next_stage = pipeline.next_stage(current_stage)
            
        if next_stage is None:
            self.build.append_message("this is the last stage of the pipeline")
            self.build.append_message("there are no more projects to launch")
            self.complete_pipeline()
            return

        # ------------------------------------------------------------------------
        # Find the projects in the next stage


        next_stage_projects = Project.objects.filter(
            pipeline = self.project.pipeline,
            stage = next_stage
        )

        self.build.append_message("next pipeline stage: %s" % next_stage.name)

        # ------------------------------------------------------------------------
        # Kick a build for all of the projects simultaneously

        if next_stage_projects.count() == 0:
            self.build.append_message("there are no projects remaining in the pipeline")
            self.build.append_message("pipeline complete!")
            self.complete_pipeline()
            return

        for p in next_stage_projects.all():
            self.build.append_message("queueing project: %s" % p.name)
            p.start(pipeline_parent_build=self.build)

        self.build.append_message("queueing complete")
