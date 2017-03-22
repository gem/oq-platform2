#!/bin/bash

#display each command before executing it
set -x
. .gem_init.sh

GIT_BRANCH="$1"
GIT_GEO_REPO="$2"
GIT_REPO="$3"
LXC_IP="$4"

sudo apt update
sudo apt install -y git python-dev python-virtualenv libpq-dev libgdal-dev openjdk-8-jdk-headless

# git clone -b "$GIT_BRANCH" https://github.com/gem/oq-platform2.git                                                                                           

## Create the virtualenv
virtualenv ~/env
source ~/env/bin/activate

cd ~

## Clone GeoNode
git clone -b "$GIT_GEO_REPO" https://github.com/GeoNode/geonode.git 

## Install GeoNode and dependencies
cd geonode
pip install -e .
pip install pygdal==1.11.3.3

## Set the local_settings.py
IP=$(ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
cat << EOF > geonode/local_settings.py
import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SITEURL = 'http://$IP:8000'
ALLOWED_HOSTS = ['$IP', 'localhost']

GEOSERVER_LOCATION = 'http://$IP:8080/geoserver/'
GEOSERVER_PUBLIC_LOCATION = 'http://$IP:8080/geoserver/'
OGC_SERVER = {
    'default': {
        'BACKEND': 'geonode.geoserver',
        'LOCATION': GEOSERVER_LOCATION,
        'LOGIN_ENDPOINT': 'j_spring_oauth2_geonode_login',
        'LOGOUT_ENDPOINT': 'j_spring_oauth2_geonode_logout',
        # PUBLIC_LOCATION needs to be kept like this because in dev mode
        # the proxy won't work and the integration tests will fail
        # the entire block has to be overridden in the local_settings
        'PUBLIC_LOCATION': GEOSERVER_PUBLIC_LOCATION,
        'USER' : 'admin',
        'PASSWORD' : 'geoserver',
        'MAPFISH_PRINT_ENABLED' : True,
        'PRINT_NG_ENABLED' : True,
        'GEONODE_SECURITY_ENABLED' : True,
        'GEOGIG_ENABLED' : False,
        'WMST_ENABLED' : False,
        'BACKEND_WRITE_ENABLED': True,
        'WPS_ENABLED' : False,
        'LOG_FILE': '%s/geoserver/data/logs/geoserver.log' % os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir)),
        # Set to dictionary identifier of database containing spatial data in DATABASES dictionary to enable
        'DATASTORE': '', #'datastore',
    }
}
EOF


## clone and setting pythonpath taxtweb
cd ~
git clone https://github.com/gem/oq-platform-taxtweb.git
cd oq-platform-taxtweb
export PYTHONPATH=$PWD

## Sync and setup GeoNode
cd ~/geonode
paver sync
paver setup

## modify local_settings with pavement from repo
cd ~/oq-platform2
ls -la
paver setup -l $LXC_IP

## Start Geonode
cd ~/geonode
paver start -b 0.0.0.0:8000


#function complete procedure for tests
exec_test () {    
    #install selenium,pip,geckodriver,clone oq-moon and execute tests with nose 
    sudo apt-get -y install python-pip wget
    sudo pip install --upgrade pip
    sudo pip install nose
    sudo pip install -U selenium==3.0.1
    wget http://ftp.openquake.org/mirror/mozilla/geckodriver-latest-linux64.tar.gz ; tar zxvf geckodriver-latest-linux64.tar.gz ; sudo cp geckodriver /usr/local/bin

    cp oq-platform2/openquake/taxonomy/test/config/moon_config.py.tmpl oq-platform2/openquake/taxonomy/test/config/moon_config.py
    git clone -b "$GIT_BRANCH" --depth=1  $GEM_GIT_REPO/oq-moon.git || git clone --depth=1 "$GEM_GIT_REPO"/oq-moon.git

    export DISPLAY=:1
    export PYTHONPATH=oq-moon:$GIT_REPO:oq-platform2/openquake/taxonomy/test/config
    python -m openquake.moon.nose_runner --failurecatcher prod -s -v --with-xunit --xunit-file=xunit-platform-prod.xml oq-platform2/openquake/taxonomy/test || true
    # sleep 40000 || true
}

#if [ "$NO_EXEC_TEST" != "notest" ] ; then
exec_test
#fi


## Stop Geonode
cd ~/geonode
sleep 4000
paver stop

