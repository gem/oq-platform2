#!/bin/bash

#display each command before executing it
set -x
. .gem_init.sh

GIT_BRANCH="$1"
GIT_GEO_REPO="$2"
GIT_REPO="$3"

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

sudo cp -Rf $HOME/"$GIT_REPO"/html/* $HOME/

## installing taxtweb
cd ~
git clone https://github.com/gem/oq-platform-taxtweb.git
cd oq-platform-taxtweb
export PYTHONPATH=$PWD

## Run GeoNode
cd ~/geonode
paver setup
paver sync
paver start -b 0.0.0.0:8000
sleep 4000
# paver stop
# kill $(ps ax | grep 'python manage.py runserver ' | grep -v 'grep' | sed 's/^ *//g;s/ .*//g' | tr '\n' ' ')

