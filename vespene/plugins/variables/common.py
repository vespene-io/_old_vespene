#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  common.py - the way build scripts are templated (and also vespene.json in
#  the build root) is templated is defined by plugins like these. 'common'
#  contains the basic behavior of sourcing in all the fields in Vespene
#  that are explicitly about variables.  This is the 'make the web UI variable
#  fields work' behavior, more or less.
#  --------------------------------------------------------------------------

import json
import traceback

class Plugin(object):
 
    def __init__(self):
        pass

    def _get_variables(self, obj):

        """
        For a given object, get all the variables in attached variable sets
        and variables together.
        """

        variables = dict()

        for x in obj.variable_sets.all():
            try:
                set_variables = json.loads(x.variables)
            except:
                #traceback.print_exc()
                raise Exception("failed to parse JSON from Variable Set (%s): %s" % (x.name, x.variables))

            if type(set_variables) == dict:
                variables.update(set_variables)
    
        try:
            obj_variables = json.loads(obj.variables)
        except:
            raise Exception("failed to parse JSON from object: %s" % obj.variables)


        if type(obj_variables) == dict:
            variables.update(obj_variables)

        return variables

    def compute(self, project, existing_variables):

        variables = dict()
        variables.update(self._get_variables(project.worker_pool))

        if project.pipeline:
            variables.update(self._get_variables(project.pipeline))

        if project.stage:
            variables.update(self._get_variables(project.stage))

        variables.update(self._get_variables(project))

        return variables
