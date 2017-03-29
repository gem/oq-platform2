#!/bin/bash

#display each command before executing it
set -x
. .gem_init.sh

GIT_BRANCH="$1"
GIT_GEO_REPO="$2"
GIT_REPO="$3"
LXC_IP="$4"

#function complete procedure for tests
exec_test () {   
    
    #install selenium,pip,geckodriver,clone oq-moon and execute tests with nose 
    sudo apt-get -y install python-pip wget
    pip install --upgrade pip
    pip install nose
    pip install -U selenium==3.0.1
    wget http://ftp.openquake.org/mirror/mozilla/geckodriver-latest-linux64.tar.gz ; tar zxvf geckodriver-latest-linux64.tar.gz ; sudo cp geckodriver /usr/local/bin

    git clone -b "$GIT_BRANCH" "$GEM_GIT_REPO/oq-moon.git" || git clone "$GEM_GIT_REPO/oq-moon.git"
    cp $GIT_REPO/openquakeplatform/test/config/moon_config.py.tmpl $GIT_REPO/openquakeplatform/test/config/moon_config.py
    
    cd $GIT_REPO
    export PYTHONPATH=../oq-moon:$PWD:$PWD/openquakeplatform/test/config:../oq-platform-taxtweb

    export DISPLAY=:1
    python -m openquake.moon.nose_runner --failurecatcher dev -s -v --with-xunit --xunit-file=xunit-platform-dev.xml openquakeplatform/test # || true
    # sleep 40000 || true
}

#
#  MAIN
#
sudo apt update
sudo apt install -y git python-dev python-virtualenv libpq-dev libgdal-dev openjdk-8-jdk-headless

git clone -b "$GIT_BRANCH" https://github.com/gem/oq-platform2.git                                                                                           

## Check if exist and  create the virtualenv
if [ ! -f ~/env/bin/activate ]; then
    virtualenv ~/env
fi

source ~/env/bin/activate

cd ~

## Clone GeoNode
git clone -b "$GIT_GEO_REPO" https://github.com/GeoNode/geonode.git 

## Install GeoNode and dependencies
cd geonode
pip install -e .
# pip install pygdal==1.11.3.3

# Install the system python-gdal
sudo apt-get install -y python-gdal

cd ~
# Create a symbolic link in your virtualenv
ln -s /usr/lib/python2.7/dist-packages/osgeo env/lib/python2.7/site-packages/osgeo

# sudo cp -Rf $HOME/"$GIT_REPO"/html/* $HOME/
sudo cp $HOME/"$GIT_REPO"/urls.py $HOME/geonode/geonode

## clone and setting pythonpath taxtweb
cd ~
git clone https://github.com/gem/oq-platform-taxtweb.git
export PYTHONPATH=~/oq-platform-taxtweb

## Sync and setup GeoNode
cd ~/geonode
paver setup

## modify local_settings with pavement from repo
cd ~/oq-platform2
paver setup -l $LXC_IP -u localhost:8080

cd ~/geonode
paver sync
paver start -b 0.0.0.0:8000

cd ~/ 
#if [ "$NO_EXEC_TEST" != "notest" ] ; then
#    exec_test
#fi


## Stop Geonode
cd ~/geonode
# paver stop

