#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  command.py - this is a plugin that runs an arbitrary CLI command when
#  a trigger event occurs.  Read the 'triggers' web documentation for
#  examples. This command will run the command string through Jinja2 prior
#  to execution, allowing for substituting in the build path, build number,
#  project name, and all kinds of other things.  For instance {{ build.working_dir }}
#  and {{ project.name }} are things you could use in the command line.
#  --------------------------------------------------------------------------

from vespene.workers import commands
from vespene.common.templates import template

class Plugin(object):

    def __init__(self, args):
        self.args = args

    def execute_hook(self, build, context):
        
        command = self.args
        command = template(command, context)
        commands.execute_command(build, command, log_command=True, output_log=False, message_log=True)
