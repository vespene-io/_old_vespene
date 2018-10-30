#!/bin/bash

source ./0_common.sh

echo "PIP=$PIP"

echo "Installing core packages..."
if [ "$DISTRO" == "redhat" ]; then
    yum -y install epel-release
    yum -y install gcc python36 python36-devel postgresql supervisor
    python36 -m ensurepip
elif [ "$DISTRO" == "ubuntu" ]; then
    apt-add-repository universe
    # apt-get update
    apt-get install -y \
      gcc \
      libssl-dev \
      postgresql \
      python3 \
      python3-pip \
      python3-setuptools \
      supervisor
elif [ "$DISTRO" == "archlinux" ]; then
    pacman --noconfirm -Sy python python-pip python-setuptools postgresql supervisor sudo
fi

echo "Setting up directories..."

mkdir -p /opt/vespene
mkdir -p /var/spool/vespene
mkdir -p /etc/vespene/settings.d/

echo "Cloning the project into /opt/vespene..."
git clone https://github.com/vespene-io/vespene.git /opt/vespene

echo "Installing python packages..."
CMD="$PYTHON -m pip install -r ../requirements.txt --trusted-host pypi.org --trusted-host files.pypi.org --trusted-host files.pythonhosted.org"
echo $CMD
$CMD
