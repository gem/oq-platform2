#!/bin/bash

#display each command before executing it
set -x
. .gem_init.sh

$branch = $1

sudo apt update
sudo apt install -y git python-dev python-virtualenv libpq-dev libgdal-dev openjdk-8-jdk-headless

git clone -b pla26 git@github.com:gem/oq-platform2.git                                                                                            

## Create the virtualenv
virtualenv ~/env
source ~/env/bin/activate

cd ~

## Clone GeoNode
git clone -b {$branch} https://github.com/GeoNode/geonode 

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

sudo cp -R $HOME/platform2/html/* $HOME/

## Run GeoNode
paver setup
paver sync
paver start -b 0.0.0.0:8000

