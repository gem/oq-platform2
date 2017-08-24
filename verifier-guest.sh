#!/bin/bash
#
# verifier-guest.sh  Copyright (c) 2017, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

set -o errtrace

#display each command before executing it
. .gem_init.sh

GIT_BRANCH="$1"
GIT_GEO_REPO="$2"
GIT_REPO="$3"
LXC_IP="$4"
GEO_DBNAME="geonode_dev"
GEO_DBUSER="geonode_dev"
GEO_DBPWD="geonode_dev"

geonode_setup_env()
{
    export PYTHONPATH=$HOME/oq-platform2:$HOME/oq-platform-taxtweb:$HOME/oq-platform-ipt
    export DJANGO_SETTINGS_MODULE='openquakeplatform.settings'
    export LOCKDOWN_GEONODE='true'
}

#function complete procedure for tests
exec_test () {   
    #install selenium,pip,geckodriver,clone oq-moon and execute tests with nose
    sudo apt-get -y install python-pip wget
    pip install --upgrade pip
    pip install nose
    wget "http://ftp.openquake.org/common/selenium-deps"
    GEM_FIREFOX_VERSION="$(dpkg-query --show -f '${Version}' firefox)"
    . selenium-deps
    wget "http://ftp.openquake.org/mirror/mozilla/geckodriver-v${GEM_GECKODRIVER_VERSION}-linux64.tar.gz"
    tar zxvf "geckodriver-v${GEM_GECKODRIVER_VERSION}-linux64.tar.gz"
    sudo cp geckodriver /usr/local/bin
    pip install -U selenium==${GEM_SELENIUM_VERSION}
    git clone -b "$GIT_BRANCH" "$GEM_GIT_REPO/oq-moon.git" || git clone -b oq-platform2 "$GEM_GIT_REPO/oq-moon.git" || git clone "$GEM_GIT_REPO/oq-moon.git"
    cp $GIT_REPO/openquakeplatform/test/config/moon_config.py.tmpl $GIT_REPO/openquakeplatform/test/config/moon_config.py
    
    # cd $GIT_REPO
    export PYTHONPATH=$HOME/oq-moon:$HOME/$GIT_REPO:$HOME/$GIT_REPO/openquakeplatform/test/config:$HOME/oq-platform-taxtweb:$HOME/oq-platform-ipt

    export DISPLAY=:1
    python -m openquake.moon.nose_runner --failurecatcher dev -s -v --with-xunit --xunit-file=xunit-platform-dev.xml $GIT_REPO/openquakeplatform/test # || true
    # sleep 40000 || true
}

rem_sig_hand() {
    trap "" ERR
    echo 'signal trapped'
    set +e
    sudo supervisorctl stop openquake-webui

    geonode_setup_env

    cd ~/geonode
    paver stop

    exit 1
}

#
#  MAIN
#
trap rem_sig_hand ERR
set -e
if [ $GEM_SET_DEBUG ]; then
    export PS4='+${BASH_SOURCE}:${LINENO}:${FUNCNAME[0]}: '
    set -x
fi


sudo apt update
sudo apt install -y git python-dev python-virtualenv libpq-dev libgdal-dev openjdk-8-jdk-headless

git clone -b "$GIT_BRANCH" https://github.com/gem/oq-platform2.git                                                                                           
## Check if exist and  create the virtualenv
if [ ! -f ~/env/bin/activate ]; then
    virtualenv ~/env
fi

source ~/env/bin/activate

cd ~

#install and configuration postgres
sudo apt-get install -y postgresql-9.5-postgis-2.2 postgresql-9.5-postgis-scripts
sudo -u postgres createdb geonode_dev
sudo -u postgres createdb geonode_dev-imports


cat << EOF | sudo -u postgres psql
    CREATE USER "$GEO_DBUSER" WITH PASSWORD '$GEO_DBPWD';
    GRANT ALL PRIVILEGES ON DATABASE "$GEO_DBNAME" to $GEO_DBUSER;
    GRANT ALL PRIVILEGES ON DATABASE "geonode_dev-imports" to $GEO_DBUSER;
EOF

sudo -u postgres psql -d geonode_dev-imports -c 'CREATE EXTENSION postgis;'
sudo -u postgres psql -d geonode_dev-imports -c 'GRANT ALL ON geometry_columns TO PUBLIC;'
sudo -u postgres psql -d geonode_dev-imports -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;'

#insert line in pg_hba.conf postgres
#sudo sed '1 i local   all             all                                md5' /etc/postgresql/9.5/main/pg_hba.conf
sudo sed -i '1 s@^@local  all             all             md5\n@g' /etc/postgresql/9.5/main/pg_hba.conf
#restart postgres
sudo service postgresql restart

#install numpy
pip install numpy shapely


## Clone GeoNode
git clone --depth=1 -b "$GIT_GEO_REPO" https://github.com/GeoNode/geonode.git

## install engine
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:openquake-automatic-team/latest-master
sudo apt-get update
sudo apt-get install -y --force-yes python-oq-engine

## Install GeoNode and dependencies
cd geonode
pip install -e .
# pip install pygdal==1.11.3.3

# Install the system python-gdal
sudo apt-get install -y python-gdal

cd ~
# Create a symbolic link in your virtualenv
ln -s /usr/lib/python2.7/dist-packages/osgeo env/lib/python2.7/site-packages/osgeo

sudo cp $HOME/"$GIT_REPO"/urls.py $HOME/geonode/geonode

## clone and setting pythonpath taxtweb and oq-platform2
cd ~

for repo in oq-platform-taxtweb oq-platform-ipt; do
    if [ "$GIT_BRANCH" = "master" ]; then false ; else git clone -b "$GIT_BRANCH" https://github.com/gem/${repo}.git ; fi || git clone -b oq-platform2 https://github.com/gem/${repo}.git || git clone https://github.com/gem/${repo}.git
done

geonode_setup_env

## Sync and setup GeoNode
cd ~/geonode

paver setup

## modify local_settings with pavement from repo
cd ~/oq-platform2
paver setup -l $LXC_IP -u localhost:8800 -s data

cd ~/geonode
paver sync
paver start -b 0.0.0.0:8000


sleep 50000

cd ~/ 
if [ "$NO_EXEC_TEST" != "notest" ] ; then
    exec_test
fi

## Stop Geonode
cd ~/geonode
sudo supervisorctl stop openquake-webui
paver stop

