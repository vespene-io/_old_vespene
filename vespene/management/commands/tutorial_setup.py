#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#---------------------------------------------------------------------------
# tutorial_setup.py - this is used manually or by the provided setup
# scripts to create some basic objects in Vespene that new users can play
# with. Once created, they can be manually deleted and aren't essential
# for day-to-day operation.
#---------------------------------------------------------------------------

import json

from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand

from vespene.models.project import Project
from vespene.models.pipeline import Pipeline
from vespene.models.stage import Stage
from vespene.models.snippet import Snippet
from vespene.models.variable_set import VariableSet
from vespene.models.worker_pool import WorkerPool
from vespene.common.logger import Logger

LOG = Logger()

EXAMPLE_REPO = "git@github.com:mpdehaan/foo.git"

EXAMPLE_BUILD_SCRIPT="""
#!/bin/bash
# This is a imaginary example build script.

# Scripts are templates and can use Jinja2 expressions:
echo "{{ welcome }}"

# Snippets can be used to supply reusable blocks of text:
{{ tutorial_snippet }}

# This project is part of a pipeline and will trigger
# other projects in this pipeline on success.

make
"""

EXAMPLE_QA_SCRIPT="""
#!/bin/bash
# this is an imaginary test script

echo "Done"
"""

EXAMPLE_STAGE_SCRIPT="""
#!/bin/bash

# this is an imaginary staging script

# FYI: did you know you can use conditionals in templates like this?:
{% if feature_flags.auto_frobnicate %}
    echo "Frobnicating..."
{% endif %}
{% if feature_flags.auto_defrobnicate %}
    echo "Defrobnicating..."
{% endif %}

echo "Done"
"""

EXAMPLE_RELEASE_SCRIPT="""
#!/bin/bash

# This is an imaginary release script and the last
# script in the pipeline.

echo "Done"
"""

EXAMPLE_SNIPPET="""

# This comes from a snippet named tutorial_snippet
# You can use snippets to import chunks of texts or scripts
# These are good to increase reuse in the build system
# This text comes from a snippet

"""



class Command(BaseCommand):
    help = 'Creates some initial objects for the tutorial experience'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        for name in [ "project1" ]:
            for suffix in [ "build", "qa", "stage", "release" ]:
                Project.objects.filter(name="tutorial-%s-%s" % (name, suffix)).delete()

        developers, _ = Group.objects.get_or_create(
            name='developers'
        )
        qa, _ = Group.objects.get_or_create(
            name='qa'
        )
        management, _ = Group.objects.get_or_create(
            name='management'
        )
        ops, _ = Group.objects.get_or_create(
            name='ops'
        )

        admins = User.objects.filter(is_superuser=True)
        user1 = admins.first()
        for x in admins.all():
            developers.user_set.add(x)
            qa.user_set.add(x)
            management.user_set.add(x)
            ops.user_set.add(x)

        if WorkerPool.objects.filter(name='tutorial-pool').count() == 0:
            worker_pool, _ = WorkerPool.objects.get_or_create(
                name='tutorial-pool',
                sudo_user='nobody',
                sudo_password='',
                isolation_method='sudo',
                variables="{}"
            )
        else:
            worker_pool = WorkerPool.objects.get(name='tutorial-pool')

        build_stage, _ = Stage.objects.get_or_create(
            name='build',
        )
        qa_stage, _ = Stage.objects.get_or_create(
            name='qa',
        )
        stage_stage, _ = Stage.objects.get_or_create(
            name='stage',
        )
        release_stage, _ = Stage.objects.get_or_create(
            name='release',
        )

        pipeline, _ = Pipeline.objects.get_or_create(
            name='tutorial-fake-CI/CD',
            stage1=build_stage,
            stage2=qa_stage,
            stage3=stage_stage,
            stage4=release_stage,
        )
        pipeline.owner_groups.add(ops)
        pipeline.save()

        p1, _ = Project.objects.get_or_create(
            name = "tutorial-project1-build",
            repo_url = EXAMPLE_REPO,
            scm_type = 'git',
            script = EXAMPLE_BUILD_SCRIPT,
            webhook_enabled = False,
            worker_pool = worker_pool,
            stage=build_stage,
            pipeline=pipeline,
            pipeline_enabled=True,
            created_by=user1,
            variables = "{}"
        )
        p2, _ = Project.objects.get_or_create(
            name = "tutorial-project1-qa",
            script = EXAMPLE_QA_SCRIPT,
            webhook_enabled = False,
            worker_pool = worker_pool,
            stage=qa_stage,
            pipeline=pipeline,
            pipeline_enabled=True,
            created_by=user1,
            variables = "{}"
        )
        p3, _ = Project.objects.get_or_create(
            name = "tutorial-project1-stage",
            script = EXAMPLE_STAGE_SCRIPT,
            webhook_enabled = False,
            worker_pool = worker_pool,
            stage=stage_stage,
            pipeline=pipeline,
            pipeline_enabled=True,
            created_by=user1,
            variables = "{}"
        )
        p4, _ =Project.objects.get_or_create(
            name = "tutorial-project1-release",
            script = EXAMPLE_RELEASE_SCRIPT,
            webhook_enabled = False,
            worker_pool = worker_pool,
            stage=release_stage,
            pipeline=pipeline,
            pipeline_enabled=True,
            created_by=user1,
            variables = "{}"
        )

        snippet, _ = Snippet.objects.get_or_create(
            name = 'tutorial_snippet',
            text = EXAMPLE_SNIPPET,
        )
        snippet.owner_groups.add(developers)
        snippet.owner_groups.add(ops)
        snippet.save()

        variable_set1, _ = VariableSet.objects.get_or_create(
            name = "tutorial-common-variables",
            variables = json.dumps(dict(
                welcome = "Welcome to the Vespene Build Tutorial",
                corp_database = "foo.example.com",
                messaging = "msg.example.com",
                password = "you should never use this for passwords! seriously, no!",
                feature_flags = dict(
                    auto_frobnicate = 1,
                    auto_defrobnicate = 0
                ),
                repo = "foo.example.com"
            ))
        )
        variable_set1.owner_groups.add(developers)
        variable_set1.owner_groups.add(ops)
        variable_set1.save()

        variable_set2, _ = VariableSet.objects.get_or_create(
            name = 'tutorial-deploy-variables',
            variables = json.dumps(dict(
                testing = 1234,
                veeblefritzer = 1
            ))
        )
        variable_set2.owner_groups.add(developers)
        variable_set2.owner_groups.add(ops)
        variable_set2.save()

        for stage in [ build_stage, qa_stage, stage_stage, release_stage ]:
            stage.variable_sets.add(variable_set1)
            stage.save()
        p4.variable_sets.add(variable_set2)
        p4.save()

        p1.owner_groups.add(developers)
        p1.owner_groups.add(ops)
        
        p2.owner_groups.add(qa)
        p2.owner_groups.add(ops)

        p3.owner_groups.add(qa)
        p3.owner_groups.add(ops)

        p4.owner_groups.add(ops)
        p4.variable_sets.add(variable_set1)
        p4.variable_sets.add(variable_set2)
        
        print("done")