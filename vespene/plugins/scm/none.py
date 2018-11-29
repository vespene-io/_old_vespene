#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  none.py - this is a SCM module that represents a build that is not
#  actually in source control. There would be nothing checked out and
#  the build script is just run as an arbitrary script.
#  --------------------------------------------------------------------------

from vespene.common.logger import Logger

LOG = Logger()

class Plugin(object):

    def __init__(self):
        pass

    def setup(self, build):
        pass

    def get_revision(self):
        return ""

    def get_last_commit_user(self):
        return ""
   
    def checkout(self):
        return ""
