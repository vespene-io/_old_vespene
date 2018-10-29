#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  commands.py - wrappers around executing shell commands
#  --------------------------------------------------------------------------

import io
import subprocess
import tempfile
import re
import json
import shlex
import shutil
import os

TIMEOUT = -1 # name of timeout command

ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')

import jinja2

from vespene.common.logger import Logger
from vespene.common.templates import Environment
from vespene.models.build import ABORTED, ABORTING, FAILURE, Build

LOG = Logger()

def check_if_can_continue(build):
    polled = Build.objects.get(pk=build.id)
    if polled.status == ABORTING:
        build.status = ABORTED
        build.save(force_update=True)
        raise Exception("Aborted")

def handle_output_variables(build, line):
    incoming = build.output_variables
    if not incoming:
        variables = dict()
    else:
        variables = json.loads(incoming)
    tokens = shlex.split(line)
    if len(tokens) != 3:
        return
    k = tokens[1]
    v = tokens[2]
    variables[k] = v
    build.output_variables = json.dumps(variables)
    build.save()

def get_timeout():

    global TIMEOUT
    if TIMEOUT != -1:
        return TIMEOUT
    if shutil.which("timeout"):
        # normal coreutils
        TIMEOUT = "timeout"
    elif shutil.which("gtimeout"):
        # homebrew coreutils
        TIMEOUT = "gtimeout"
    else:
        TIMEOUT = None
    return TIMEOUT

def execute_command(build, command, input_text=None, env=None, log_command=True, output_log=True, message_log=False, timeout=None):
    """
    Execute a command (a list or string) with input_text as input, appending
    the output of all commands to the build log.
    """

    timeout_cmd = get_timeout()

    shell = True
    if type(command) == list:
        if timeout and timeout_cmd:
            command.insert(0, timeout)
            command.insert(0, timeout_cmd)
        shell = False
    else:
        if timeout and timeout_cmd:
            command = "%s %s %s" % (timeout_cmd, timeout, command)

    sock = os.environ.get('SSH_AUTH_SOCK', None)
    if env and sock:
        env['SSH_AUTH_SOCK'] = sock

    if log_command:
        LOG.debug("executing: %s" % command)
        if build:
            build.append_message(command)

    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell, env=env)

    if input_text is None:
        input_text = ""

    stdin = io.TextIOWrapper(
        process.stdin,
        encoding='utf-8',
        line_buffering=True,
    )
    stdout = io.TextIOWrapper(
        process.stdout,
        encoding='utf-8',
    )
    stdin.write(input_text)
    stdin.close()

    out = ""
    for line in stdout:

        line = ansi_escape.sub('', line)

        if build:
            check_if_can_continue(build)
            if output_log:
                build.append_output(line)
            if message_log:
                build.append_message(line)
        out = "" + line

        if line.startswith("vespene/set"):
            handle_output_variables(build, line)

    process.wait()

    if process.returncode != 0:
        build.append_message("build failed with exit code %s" % process.returncode)
        build.status = FAILURE
        build.return_code = process.returncode
        build.save(force_update=True)
        raise Exception("Failed")
    return out
        
def answer_file(answer):
    (_, fname) = tempfile.mkstemp()
    fh = open(fname, "w")
    fh.write("#!/bin/bash\n")
    fh.write("echo %s" % answer);
    fh.close()
    return fname
