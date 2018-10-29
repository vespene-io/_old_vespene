#!/bin/bash

# ---------------------------------------------------------------------------
# 4_superuser.sh: prompt the user to create an admin account. Run this on any Vespene
# machine with database access.
# ---------------------------------------------------------------------------

# load common settings
source ./0_common.sh

# run the django management command (this is interactive)
cd /opt/vespene
$PYTHON manage.py createsuperuser
