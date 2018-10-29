#!/bin/bash

source ./0_common.sh

echo "PIP=$PIP"

echo "Installing core packages..."
if [ "$DISTRO" == "redhat" ]; then
    yum -y install epel-release
    yum -y install gcc python36 python36-devel postgresql supervisor
    python36 -m ensurepip
elif [ "$DISTRO" == "ubuntu" ]; then
    sudo apt-add-repository universe
    # apt-get update
    apt-get install -y python3 python3-setuptools python3-pip gcc postgresql supervisor
fi

echo "Setting up directories..."

mkdir -p /opt/vespene
mkdir -p /var/spool/vespene
mkdir -p /etc/vespene/settings.d/

echo "Cloning the project into /opt/vespene..."
git clone https://github.com/mpdehaan/vespene.git /opt/vespene

echo "Installing python packages..."
CMD="$PIP install -r ../../requirements.txt --trusted-host pypi.org --trusted-host files.pypi.org --trusted-host files.pythonhosted.org"
echo $CMD
$CMD



