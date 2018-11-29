#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  svn.py - this code contains support for the old-and-busted Subversion
#  version control system, for those that are not yet using git, which
#  is the new hotness.  It currently assumes repos are publically accessible
#  and because SVN doesn't really have "real" branches, ignores the
#  branch parameter. Upgrades from users of SVN setups are quite welcome as
#  are additions of other SCM types.
#  --------------------------------------------------------------------------

import shlex

from vespene.common.logger import Logger
from vespene.workers import commands

LOG = Logger()

class Plugin(object):

    def __init__(self):
        pass

    def setup(self, build):
        self.build = build
        self.project = build.project
        self.repo = build.project.repo_url

    def info_extract(self, attribute):
        cmd = "(cd %s; svn info | grep \"%s\")" % (self.build.working_dir, attribute)
        out = commands.execute_command(self.build, cmd, output_log=False, message_log=True)
        if ":" in out:
            return out.split(":")[-1].strip()
        return None

    def get_revision(self):
        return self.info_extract("Last Changed Rev:")

    def get_last_commit_user(self):
        return self.info_extract("Last Changed Author:")

    def checkout(self):
        self.build.append_message("----------\nCloning repository...")
        cmd = "svn checkout --non-interactive --quiet %s %s" % (shlex.quote(self.repo), self.build.working_dir)
        return commands.execute_command(self.build, cmd, output_log=False, message_log=True)
