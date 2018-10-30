# --
# /etc/vespene/settings.d/database.py info
# --

# Database configuration
# the local database is fine for an initial deployment
# be sure to change the password!
DBSERVER="127.0.0.1"
DBPASS="vespene!"

# --
# webserver info
# --

# options to feed to gunicorn in /etc/vespene/supervisord.conf
# if you change this to 0.0.0.0 to bind to all addresses be
# sure to set up SSL

GUNICORN_OPTS="--bind 127.0.0.1:8000"

# --
# /etc/vespene/settings.d/build.py info
# --

BUILDROOT="/tmp/vespene"

# ---
# /etc/vespene/supervisord.conf info
# ---

# Should this machine be running any workers? 
# This is a space separated string of key=value pairs where the name is a 
# worker pool name (configured in the Vespene UI) and the value is the number of copies 
# of that worker to run. Increasing the number increases parallelism.

# WORKER_CONFIG="general=2 tutorial-pool=1"
WORKER_CONFIG="tutorial-pool=1"

# rough OS detection for now; patches accepted!
if [ "$OSTYPE" == "linux-gnu" ]; then
   if [ -f /etc/redhat-release ]; then
      DISTRO="redhat"
      PIP="/usr/local/bin/pip3.6"
      PYTHON="/usr/bin/python3.6"
   elif [ -f /usr/bin/apt ]; then
      DISTRO="ubuntu"
      PYTHON="/usr/bin/python3"
      PIP="/usr/bin/pip3"
   elif [ -f /usr/bin/pacman ]; then
      DISTRO="archlinux"
      PYTHON="/usr/bin/python"
      PIP="/usr/bin/pip"
   fi
elif [ -f /usr/local/bin/brew ]; then
      DISTRO="MacOS"
      PYTHON="/usr/local/bin/python3"
      PIP="/usr/local/bin/pip3"
else
   echo "this OS may work with Vespene but we don't have setup automation for this just yet"
   DISTRO="?"
fi
