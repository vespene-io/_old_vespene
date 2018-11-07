#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  ssh_agent.py - Vespene workers are run wrapped by 'ssh-agent' processes
#  and the workers can use SSH keys configured per project to do SCM checkouts
#  or use SSH-based automation. This is mostly handled right now
#  through basic expect scripts and does support password-locked keys.
#  --------------------------------------------------------------------------

import os
import tempfile

from vespene.common.logger import Logger
from vespene.workers import commands

LOG = Logger()

# =============================================================================

class SshAgentManager(object):

    def __init__(self, builder, build):
        self.builder = builder
        self.build = build
        self.project = self.build.project
        self.tempfile_paths = []

    def add_all_keys(self):
        for access in self.project.ssh_keys.all():
            self.add_key(access)

    def add_key(self, access):

        (_, keyfile) = tempfile.mkstemp()
        answer_file = None

        try:
            fh = open(keyfile, "w")
            private = access.get_private_key()
            fh.write(private)
            fh.close()

            answer_file = None


            if access.unlock_password:
                LOG.debug("adding SSH key with passphrase!")
                self.ssh_add_with_passphrase(keyfile, access.get_unlock_password())
            else:
                if ',ENCRYPTED' in private:
                    raise Exception("SSH key has a passphrase but an unlock password was not set. Aborting")
                LOG.debug("adding SSH key without passphrase!")
                self.ssh_add_without_passphrase(keyfile)
        finally:
            os.remove(keyfile)
            if answer_file:
                os.remove(answer_file)
  
    def cleanup(self):
        # remove SSH identities
        LOG.debug("removing SSH identities")
        commands.execute_command(self.build, "ssh-add -D", log_command=False, message_log=False, output_log=False)    

    def ssh_add_without_passphrase(self, keyfile):  
        LOG.debug(keyfile)
        cmd = "ssh-add %s < /dev/null" % keyfile
        commands.execute_command(self.build, cmd, env=None, log_command=False, message_log=False, output_log=False)

    def ssh_add_with_passphrase(self, keyfile, passphrase):
        (_, fname) = tempfile.mkstemp()
        fh = open(fname, "w")
        script = """
        #!/usr/bin/expect -f
        spawn ssh-add %s
        expect "Enter passphrase*:"
        send "%s\n";
        expect "Identity added*"
        interact
        """ % (keyfile, passphrase)
        fh.write(script)
        fh.close()
        commands.execute_command(self.build, "/usr/bin/expect -f %s" % fname, output_log=False, message_log=False)
        os.remove(fname)
        return fname
