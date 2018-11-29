#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  pipelines.py - this logic allows the variables output (see web pipeline docs) in
#  the build textual output to be used as input variables to future pipeline
#  steps. It's useful if using pipelines and wanting to do something like making
#  a deployment step aware of an AWS image ID that got built in a previous step.
#  --------------------------------------------------------------------------

import json
from vespene.models.project import Project

class Plugin(object):
     
 
    def __init__(self):
        pass

    def compute(self, project, existing_variables):
        """
        Get all the variables to pass to Jinja2 for a given project, including snippets.
        (This is the variable precedence algorithm, right here).
        """

        output_variables = dict()
        if project.pipeline and project.stage:
            stage = project.stage
            for previous_stage in project.pipeline.all_previous_stages(stage):
                previous_projects = Project.objects.filter(pipeline=project.pipeline, stage=previous_stage).all()
                for previous in previous_projects:
                    last = previous.last_successful_build
                    if not last:
                        continue
                    try:
                        variables = json.loads(last.output_variables)
                    except:
                        variables = dict()
                    if variables:
                        output_variables.update(variables)
        return output_variables
