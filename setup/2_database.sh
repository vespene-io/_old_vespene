#!/bin/bash

# ---------------------------------------------------------------------------
# 2_database.sh: common settings used by the for Vespene setup scripts.
# This file is loaded by the the other setup scripts and just contains variables.
# ---------------------------------------------------------------------------

# load common settings
source ./0_common.sh

echo "installing packages..."
# install postgresql
if [[ "$DISTRO" == "redhat" ]]; then
   yum -y install postgresql-server
   CONFIG="/var/lib/pgsql/data/pg_hba.conf"
elif [[ "$IDSTRO" == "ubuntu" ]]; then
   apt install -y postgresql postgresql-contrib
   CONFIG="/etc/postgresql/10/main/pg_hba.conf"
elif [[ "$DISTRO" == "archlinux" ]]; then
   CONFIG="/var/lib/postgres/data/pg_hba.conf"
fi

echo "initializing the database server..."
if [[ "$DISTRO" == "archlinux" ]]; then
    sudo -u postgres initdb -D '/var/lib/postgres/data'
else
    sudo -u postgres postgresql-setup initdb
fi

echo "configuring security..."
# configure PostgreSQL security to allow the postgres account in locally, and allow
# password access remotely.  You can tweak this if you want but must choose something
# that will work with the /etc/vespene/settings.d/database.py that will be created.
# Using password auth is highly recommended as the workers also use database access.
cat > "$CONFIG" <<'END_OF_CONF'
local	all	postgres	ident
host	all	all	0.0.0.0/0	md5
END_OF_CONF

echo "starting postgresql..."
# start the PostgreSQL service using systemd
systemctl enable postgresql.service
systemctl start postgresql.service

echo "creating the vespene database and user..."
echo "  (if you any errors from 'cd' here or further down they can be ignored)"

EXISTS=`sudo -u postgres psql -lqt | grep vespene`
if [ $? -eq 1 ]; then
   sudo -u postgres createdb vespene
   echo "creating the vespene user"
   sudo -u postgres createuser vespene
else
   echo "- database already exists"
fi

echo "granting access..."
# give the user access and set their password
sudo -u postgres psql -U postgres -d vespene -c "GRANT ALL on DATABASE vespene TO vespene"
sudo -u postgres psql -U postgres -d vespene -c "ALTER USER vespene WITH ENCRYPTED PASSWORD '$DBPASS'"
