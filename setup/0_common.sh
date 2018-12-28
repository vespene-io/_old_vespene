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
# sure to set up SSL. This will run as non-root so chose
# a non-privileged port if adjusting the default. Proxying
# with NGINX or Apache later is also an option.

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

# how do you need to sudo to run the python management commands?
APP_SUDO="sudo"

# how do you need to sudo to run postgresql management commands?
POST_SUDO="sudo -u postgres"

# what filesystem user should own the postgresql data directory?
DB_USER="postgres"

# what user should be running Vespene itself?
APP_USER="vespene"

# rough OS detection for now; patches accepted!
DISTRO="?"
if [[ "$OSTYPE" == "linux-gnu" ]]; then
   if [ -f /etc/redhat-release ]; then
      echo "detected RHEL/CentOS"
      DISTRO="redhat"
      PIP="/usr/local/bin/pip3.6"
      PYTHON="/usr/bin/python3.6"
   elif [[ -f /etc/system-release && "$(cat /etc/system-release)" =~ "Amazon Linux release 2" ]]; then
      echo "detected Amazon Linux 2"
      DISTRO="amazon2"
      PIP="/usr/local/bin/pip3.6"
      PYTHON="/usr/bin/python3.6"
   elif [ -f /usr/bin/zypper ]; then
      echo "detected openSUSE"
      DISTRO="opensuse"
      PYTHON="/usr/bin/python3"
      PIP="/usr/bin/pip3"
   elif [ -f /usr/bin/apt ]; then
      echo "detected Ubuntu/Debian"
      DISTRO="ubuntu"
      PYTHON="/usr/bin/python3"
      PIP="/usr/bin/pip3"
   elif [ -f /usr/bin/pacman ]; then
      echo "detected Arch Linux"
      DISTRO="archlinux"
      PYTHON="/usr/bin/python"
      PIP="/usr/bin/pip"
   fi
elif [[ "$OSTYPE" == "linux-musl" ]]; then
    if [ -f /etc/alpine-release ]; then
      echo "detected Alpine Linux"
      DISTRO="alpine"
      PYTHON="/usr/bin/python3"
      PIP="/usr/bin/pip3"
    fi
elif [ -f /usr/local/bin/brew ]; then
      echo "detected MacOS"
      DISTRO="MacOS"
      PYTHON="/usr/local/bin/python3"
      PIP="/usr/local/bin/pip3"
      APP_SUDO=""
      POST_SUDO=""
      DB_USER=`whoami`
      APP_USER=`whoami`
else
   echo "this OS may work with Vespene but we don't have setup automation for this just yet"
   DISTRO="?"
fi

me=`whoami`
if [[ "$me" == "root" ]]; then
    echo "*** please re-run this script from a user account with sudo rights"
    exit 1
fi
