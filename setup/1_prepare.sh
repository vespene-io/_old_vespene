#!/bin/bash

source ./0_common.sh

echo "PIP=$PIP"

echo "Installing core packages..."
if [ "$DISTRO" == "redhat" ]; then
    sudo yum -y install epel-release
    sudo yum -y install gcc python36 python36-devel postgresql supervisor
    sudo python36 -m ensurepip
elif [ "$DISTRO" == "opensuse" ]; then
    zypper refresh
    zypper install -y gcc python python-pip python3 python3-pip python3-setuptools postgresql
    python2.7 -m pip install supervisor
elif [ "$DISTRO" == "ubuntu" ]; then
    sudo apt-add-repository universe
    sudo apt-get update
    sudo apt-get install -y gcc libssl-dev postgresql-client python3 python3-pip python3-setuptools supervisor
elif [ "$DISTRO" == "archlinux" ]; then
    sudo pacman --noconfirm -Sy python python-pip python-setuptools postgresql supervisor sudo
elif [ "$DISTRO" == "MacOS" ]; then
    brew install python@3 postgresql supervisor
fi

if [ "$DISTRO" != "MacOS" ]; then
    sudo useradd vespene
fi

echo "Setting up directories..."

sudo mkdir -p /opt/vespene
sudo mkdir -p /var/spool/vespene
sudo mkdir -p /etc/vespene/settings.d/
sudo mkdir -p /var/log/vespene/

echo "Cloning the project into /opt/vespene..."
rm -rf /opt/vespene/*
sudo cp -a ../* /opt/vespene

echo "APP_USER=$APP_USER"
sudo chown -R $APP_USER /opt/vespene
sudo chown -R $APP_USER /var/spool/vespene
sudo chown -R $APP_USER /etc/vespene/settings.d/
sudo chown -R $APP_USER /var/log/vespene

echo "Installing python packages..."
CMD="sudo $PYTHON -m pip install -r ../requirements.txt --trusted-host pypi.org --trusted-host files.pypi.org --trusted-host files.pythonhosted.org"
echo $CMD
$CMD
