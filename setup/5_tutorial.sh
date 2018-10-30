#!/bin/bash

# ---------------------------------------------------------------------------
# 5_tutorial.sh: sets up basic objects used in the tutorial, so Vespene isn't "blank" when you first log in.
# these objects can be deleted later.
# ---------------------------------------------------------------------------

# this also creates a worker pool named "tutorial-pool" so one of our configured background
# processes has something to do.

# load common settings
source ./0_common.sh

# run the custom management command that creates the objects
cd /opt/vespene
$APP_SUDO $PYTHON manage.py tutorial_setup


