#!/bin/bash

# ---------------------------------------------------------------------------
# 2_database.sh: common settings used by the for Vespene setup scripts.
# This file is loaded by the the other setup scripts and just contains variables.
# ---------------------------------------------------------------------------

# load common settings
source ./0_common.sh

# ---
echo "installing packages ..."
CONFIG=""

# install postgresql
if [[ "$DISTRO" == "redhat" ]]; then
   sudo yum -y install postgresql-server
   CONFIG="/var/lib/pgsql/data/pg_hba.conf"
elif [[ "$DISTRO" == "ubuntu" ]]; then
   sudo apt install -y postgresql postgresql-contrib
   CONFIG="/etc/postgresql/10/main/pg_hba.conf"
elif [[ "$DISTRO" == "archlinux" ]]; then
   sudo pacman --noconfirm -Sy postgresql
   CONFIG="/var/lib/postgres/data/pg_hba.conf"
elif [[ "$DISTRO" == "MacOS" ]]; then
   CONFIG="/usr/local/var/postgres/pg_hba.conf"
fi

# ---
echo "initializing the database server..."

if [[ "$DISTRO" == "archlinux" ]]; then
    sudo -u postgres initdb -D '/var/lib/postgres/data'
elif [[ "$DISTRO" == "MacOS" ]]; then
    initdb /usr/local/var/postgres
elif [[ "$DISTRO" == "redhat" ]]; then
    sudo -u postgres postgresql-setup initdb
else
    echo "initdb should not be needed on this platform"
fi

# ----
echo "configuring security at ${CONFIG} ..."

# configure PostgreSQL security to allow the postgres account in locally, and allow
# password access remotely.  You can tweak this if you want but must choose something
# that will work with the /etc/vespene/settings.d/database.py that will be created.
# Using password auth is highly recommended as the workers also use database access.
sudo tee $CONFIG > /dev/null <<END_OF_CONF
local	all	${DB_USER}	ident
host	all	all	0.0.0.0/0	md5
END_OF_CONF

sudo chown $DB_USER $CONFIG

# ---
echo "starting postgresql..."
if [ "$OSTYPE" == "linux-gnu" ]; then
# start the PostgreSQL service using systemd
    sudo systemctl enable postgresql.service
    sudo systemctl start postgresql.service
elif [ "$DISTRO" == "MacOS" ]; then
    /usr/local/bin/pg_ctl restart -D /usr/local/var/postgres/
fi

# --
echo "creating the vespene database and user..."
echo "  (if you any errors from 'cd' here or further down they can be ignored)"

EXISTS=`sudo -u $DB_USER psql -lqt | grep vespene`
if [ $? -eq 1 ]; then
   $POST_SUDO createdb vespene
   echo "creating the vespene user"
   $POST_SUDO createuser vespene
else
   echo "- database already exists"
fi

# --
echo "granting access..."
# give the user access and set their password
$POST_SUDO psql -d vespene -c "GRANT ALL on DATABASE vespene TO vespene"
$POST_SUDO psql -d vespene -c "ALTER USER vespene WITH ENCRYPTED PASSWORD '$DBPASS'"
