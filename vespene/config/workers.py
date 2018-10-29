#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
# ---------------------------------------------------------------------------
# workers.py - configuration related to worker setup.  This file *CAN* be
# different per worker.
# ---------------------------------------------------------------------------

BUILD_ROOT = "/tmp/vespene/buildroot/"

# ---------------------------------------------------------------------------
# all of these settings deal with serving up the buildroot.

# to disable file serving thorugh Django you can set this to FALSE

FILESERVING_ENABLED = True

FILESERVING_PORT = 8000

# leave this blank and the system will try to figure this out
# the setup scripts will usually set this to `hostname` though if
# unset the registration code will run `hostname`
FILESERVING_HOSTNAME = ""

FILESERVING_URL="/srv"

# if you disable fileserving but are using triggers to copy build roots
# to some other location (perhaps NFS served up by a web server or an FTP
# server) you can set this FILESERVING_ENABLED to False and the following pattern will
# be used instead to generate web links in the main GUI. If this pattern
# is set the links to the built-in fileserver will NOT be rendered, but this will
# not turn on the fileserver.  To do that, set FILESERVING_ENABLED to False also

# BUILDROOT_WEB_LINK  = "http://build-fileserver.example.com/builds/{{ build.id }}"
BUILDROOT_WEB_LINK = ""
