#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  snippets.py - this rather simple plugin makes snippets available to
#  Jinja2 as variables. Snippet names containing "-" or " " aren't valid Python 
#  variable so we replace those characters. We may need to make this replacement
#  smarter in the future, but it is a start.
#  --------------------------------------------------------------------------

from vespene.models.snippet import Snippet
from vespene.common.templates import template

class Plugin(object):

    def __init__(self):
        pass 

    def compute(self, project, existing_variables):
        """
        We have to Jinja2-evaluate all the snippets before injecting them into
        the dictionary for the build script evaluation.
        """

        results = dict()
        for x in Snippet.objects.order_by('name').all():
            # FIXME: on error, load something into the template an empty string and log it
            name = x.name.replace("-","_").replace(" ","_")
            results[name] = template(x.text, existing_variables, strict_undefined=False)
        return results
