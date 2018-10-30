# --
# /etc/vespene/settings.d/database.py info
# --

# Please change these settings!
DBSERVER="127.0.0.1"
DBPASS="vespene!"

# --
# /etc/vespene/settings.d/build.py info
# --

BUILDROOT="/tmp/vespene"

# ---
# /etc/vespene/supervisord.conf info
# ---

# Should this machine be running the Vespene webUI?
IS_CONTROLLER="true"

# Should this machine be running any workers, this is a space separated 
# string of key=value pairs where the name is a worker pool name 
# (configured in the Vespene UI) and the value is the number of copies 
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
else
   echo "this OS may work with Vespene but we don't have setup automation for this just yet"
   DISTRO="?"
fi
