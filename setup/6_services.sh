#!/bin/bash

# ---------------------------------------------------------------------------
# 6_services.sh: sets up supervisor to start the various worker processes, if any are configured. The tutorial example typically
# sets up a worker called "tutorial-pool", though you can have any number of them. To change these later, edit
# the supervisor configuration in /etc/vespene/ and restart the vespene systemd service.

# workers are coded so that if they don't have an object in the Vespene database yet those processes will sleep and wake
# up every minute until they do.  So if you created some named workers here you still need to create those names in the
# Vespene UI before they can start doing any work.
# ---------------------------------------------------------------------------

# load common config settings

source ./0_common.sh

# ---
# generate the supervisor configuration

echo "generating supervisor config..."
cd /opt/vespene
sudo $PYTHON manage.py generate_supervisor --path /etc/vespene/supervisord.conf --workers "$WORKER_CONFIG" --executable=$PYTHON --source /opt/vespene --gunicorn "$GUNICORN_OPTS"
echo "creating init script..."
sudo chown -R $APP_USER /etc/vespene/

# --
# bail if on a Mac
if [ "$DISTRO" == "MacOS" ]; then
   echo "launch supervisor with: supervisord -n c /etc/vespene/supervisord.conf"
   exit 0
fi


# ---
# generate systemd init script

sudo tee /etc/systemd/system/vespene.service </dev/null <<END_OF_SYSTEMD
[Unit]
Description=Vespene Services
Documentation=http://vespene.io
After=postgresql.service

[Service]
Type=Simple
ExecStart=/usr/bin/supervisord -n -c /etc/vespene/supervisord.conf
#ExecStop=/usr/bin/supervisorctl $OPTIONS shutdown
#ExecReload=/usr/bin/supervisorctl -c /etc/vespene/supervisord.conf $OPTIONS reload
KillMode=process
Restart=on-failure
RestartSec=50s
User=${APP_USER}

[Install]
WantedBy=multi-user.target
END_OF_SYSTEMD

echo "starting the service..."
# start the service
sudo systemctl daemon-reload
sudo systemctl start vespene.service
sudo systemctl enable vespene.service

echo "Vespene is now running on port 8000"
