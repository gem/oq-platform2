#!/bin/bash
#
# verifier-guest.sh  Copyright (c) 2017, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# HOW TO CALL FOR REINSTALL FROM verifier.sh:
#
# cp oq-platform2/verifier-guest.sh .
# export GEM_SET_DEBUG=\"$GEM_SET_DEBUG\"
# export GEM_GIT_REPO=\"$GEM_GIT_REPO\"
# export GEM_GIT_PACKAGE=\"$GEM_GIT_PACKAGE\"
# export GEM_TEST_LATEST=\"$GEM_TEST_LATEST\"

# \"./verifier-guest.sh\" \"$branch_id\" \"$branch_geonode\" \"$GEM_GIT_PACKAGE\" \"$lxc_ip\" \"$notests\"


sudo systemctl stop apt-daily.timer

set -o errtrace

#display each command before executing it
. .gem_init.sh

REINSTALL=
if [ "$1"  = "-r" -o "$1" = "--reinstall" ]; then
    REINSTALL=true
    shift
fi
GIT_BRANCH="$1"
GIT_GEO_REPO="$2"
GIT_REPO="$3"
LXC_IP="$4"
GEO_DBNAME="geonode_dev"
GEO_DBUSER="geonode_dev"
GEO_DBPWD="geonode_dev"
GEO_STABLE_HASH="aa5932d"

geonode_setup_env()
{
    export PYTHONPATH=$HOME/oq-platform2:$HOME/oq-platform-taxtweb:$HOME/oq-platform-ipt:$HOME/oq-platform-building-class
    #export DJANGO_SETTINGS_MODULE='openquakeplatform.settings'
    export LOCKDOWN_GEONODE='true'
}

#install dependencies vulnerability and ipt
extra_deps_install() {
    python -m pip install "django<2"
    pip install django-nested-inline
    pip install django_extras
    pip install -e git+git://github.com/gem/django-chained-selectbox.git@pla26#egg=django-chained-selectbox-0.2.2
    pip install -e git+git://github.com/gem/django-nested-inlines.git@pla26#egg=django-nested-inlines-0.1.4
    pip install -e git+git://github.com/gem/django-chained-multi-checkboxes.git@pla26#egg=django-chained-multi-checkboxes-0.4.1
    pip install -e git+git://github.com/gem/wadofstuff-django-serializers.git@pla26#egg=wadofstuff-django-serializers-1.1.2
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
    if [ -z "$REINSTALL" ]; then
        git clone -b "$GIT_BRANCH" "$GEM_GIT_REPO/oq-moon.git" || git clone -b oq-platform2 "$GEM_GIT_REPO/oq-moon.git" || git clone "$GEM_GIT_REPO/oq-moon.git"
    fi
    cp $GIT_REPO/openquakeplatform/test/config/moon_config.py.tmpl $GIT_REPO/openquakeplatform/test/config/moon_config.py
    
    # cd $GIT_REPO
    export PYTHONPATH=$HOME/oq-moon:$HOME/$GIT_REPO:$HOME/$GIT_REPO/openquakeplatform/test/config:$HOME/oq-platform-taxtweb:$HOME/oq-platform-ipt:$HOME/oq-platform-building-class

    export GEM_OPT_PACKAGES="$(python -c 'from openquakeplatform.settings import STANDALONE_APPS ; print(",".join(x for x in STANDALONE_APPS))')"

    export GEM_PLA_ADMIN_ID=1000

    export DISPLAY=:1
    python -m openquake.moon.nose_runner --failurecatcher dev -s -v --with-xunit --xunit-file=xunit-platform-dev.xml $GIT_REPO/openquakeplatform/test # || true

}

rem_sig_hand() {
    trap "" ERR
    echo 'signal trapped'
    set +e
    sudo supervisorctl stop openquake-webui

    geonode_setup_env

    cd ~/geonode
    paver -f $HOME/$GIT_REPO/pavement.py stop

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

# Used a local clone (see verifier.sh)
# git clone -b "$GIT_BRANCH" https://github.com/gem/oq-platform2.git

# if reinstall try to turn off all running daemon
if [ "$REINSTALL" ]; then
    if [ -f ~/env/bin/activate -a -f ~/oq-platform2/pavement.py -a -d ~/geonode ]; then
        . ~/env/bin/activate
        cd ~/geonode
        sudo supervisorctl stop openquake-webui || true
        paver -f ~/oq-platform2/pavement.py stop || true
        deactivate
    else
        echo "Reinstall required but ~/env/bin/activate, ~/oq-platform2/pavement.py or ~/geonode doesn't exists"
        read -p "Press Enter to continue or Ctrl+C to interrupt the installation"
    fi
fi


## Check if exist and  create the virtualenv
if [ -d ~/env ]; then
    rm -rf ~/env
fi
virtualenv ~/env


source ~/env/bin/activate

# install nested applications
extra_deps_install

pip install scipy

cd ~

#install and configuration postgres
sudo apt-get install -y postgresql-9.5-postgis-2.2 postgresql-9.5-postgis-scripts curl xmlstarlet supervisor
if [ "$REINSTALL" ]; then
    sudo -u postgres dropdb geonode_dev
    sudo -u postgres dropdb geonode_dev-imports
fi
sudo -u postgres createdb geonode_dev
sudo -u postgres createdb geonode_dev-imports

cat << EOF | sudo -u postgres psql
    CREATE USER "$GEO_DBUSER" WITH PASSWORD '$GEO_DBPWD';
    GRANT ALL PRIVILEGES ON DATABASE "$GEO_DBNAME" to $GEO_DBUSER;
    GRANT ALL PRIVILEGES ON DATABASE "geonode_dev-imports" to $GEO_DBUSER;
EOF

sudo -u postgres psql -d geonode_dev -c 'CREATE EXTENSION postgis;'
sudo -u postgres psql -d geonode_dev -c 'GRANT ALL ON geometry_columns TO PUBLIC;'
sudo -u postgres psql -d geonode_dev -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;'

sudo -u postgres psql -d geonode_dev-imports -c 'CREATE EXTENSION postgis;'
sudo -u postgres psql -d geonode_dev-imports -c 'GRANT ALL ON geometry_columns TO PUBLIC;'
sudo -u postgres psql -d geonode_dev-imports -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;'

#insert line in pg_hba.conf postgres
if ! sudo head -n 1 /etc/postgresql/9.5/main/pg_hba.conf | grep -q "local \+all \+$GEO_DBUSER \+md5"; then
    sudo sed -i '1 s@^@local  all             '"$GEO_DBUSER"'             md5\n@g' /etc/postgresql/9.5/main/pg_hba.conf
fi
#restart postgres
sudo service postgresql restart

#install numpy
pip install numpy

## Clone GeoNode
if [ -z "$REINSTALL" ]; then
    if [ "$GEM_TEST_LATEST" = "true" ]; then
        git clone --depth=1 -b "$GIT_GEO_REPO" https://github.com/GeoNode/geonode.git
    else
        git clone -n https://github.com/GeoNode/geonode.git
        cd geonode
        git checkout "$GEO_STABLE_HASH"
        cd ..
    fi
else
    cd geonode
    git clean -dfx
    cd -
fi

## install engine
sudo apt-get install -y software-properties-common
# sudo add-apt-repository -y ppa:openquake-automatic-team/latest-master
sudo add-apt-repository -y ppa:openquake/release-3.0
sudo apt-get update
sudo apt-get install -y --force-yes python-oq-engine

## Install GeoNode and dependencies
cd geonode
pip install -r requirements.txt

if [ "$GEM_TEST_LATEST" != "true" ]; then
    ## more stable dependencies installed
    pip install -r $HOME/$GIT_REPO/gem_geonode_requirements.txt
fi

pip install -e .

# Install the system python-gdal
sudo apt-get install -y python-gdal

cd ~
# Create a symbolic link in your virtualenv
ln -sf /usr/lib/python2.7/dist-packages/osgeo env/lib/python2.7/site-packages/osgeo

## clone and setting pythonpath taxtweb, ipt, oq-platform2
cd ~

if [ -z "$REINSTALL" ]; then
    for repo in oq-platform-taxtweb oq-platform-ipt oq-platform-building-class; do
        # for repo in oq-platform-taxtweb; do
        if [ "$GIT_BRANCH" = "master" ]; then false ; else git clone -b "$GIT_BRANCH" https://github.com/gem/${repo}.git ; fi || git clone -b oq-platform2 https://github.com/gem/${repo}.git || git clone https://github.com/gem/${repo}.git
    done
fi

## Setup environment
geonode_setup_env

## Clone oq-private
# git clone git@gitlab.openquake.org:openquake/oq-private.git

## Sync and setup GeoNode
cd ~/geonode

paver -f $HOME/$GIT_REPO/pavement.py setup

## Create local_settings with pavement from repo
paver -f $HOME/$GIT_REPO/pavement.py oqsetup -l $LXC_IP -u localhost:8800 -s /home/ubuntu/geonode/data

python manage.py migrate account --noinput
paver -f $HOME/$GIT_REPO/pavement.py sync
paver -f $HOME/$GIT_REPO/pavement.py start -b 0.0.0.0:8000

## Symbolic link to solve spatialite warning of Geoserver
sudo ln -sf /usr/lib/x86_64-linux-gnu/libproj.so.9 /usr/lib/x86_64-linux-gnu/libproj.so.0

## Stop Geoserver before rename postgres jar
paver stop_geoserver

## Rename postgres jar in WEB-INF of Geoserver
if [ -f $HOME/geonode/geoserver/geoserver/WEB-INF/lib/postgresql-9.4.1211.jar ]; then
    mv $HOME/geonode/geoserver/geoserver/WEB-INF/lib/postgresql-9.4.1211.jar $HOME/geonode/geoserver/geoserver/WEB-INF/lib/old_postgresql-9.4.1211.jar
fi

## Start Geoserver after rename postgres jar
paver start_geoserver

## Create vulnerability groups
python ./manage.py import_vuln_geo_applicability_csv $HOME/$GIT_REPO/openquakeplatform/vulnerability/dev_data/vuln_geo_applicability_data.csv
python ./manage.py vuln_groups_create

## load data and install simplejson for vulnerability application
python ./manage.py loaddata $HOME/$GIT_REPO/openquakeplatform/vulnerability/post_fixtures/initial_data.json
pip install simplejson==2.0.9

## load data for gec and isc viewer
python ./manage.py import_isccsv $HOME/$GIT_REPO/openquakeplatform/isc_viewer/dev_data/isc_data.csv  $HOME/$GIT_REPO/openquakeplatform/isc_viewer/dev_data/isc_data_app.csv

python ./manage.py import_gheccsv $HOME/$GIT_REPO/openquakeplatform/ghec_viewer/dev_data/ghec_data.csv

## Create Gem user
python ./manage.py create_gem_user

## Add other users
python ./manage.py add_user $HOME/oq-platform2/openquakeplatform/common/gs_data/dump/auth_user.json

## Add Gem category
python ./manage.py loaddata $HOME/$GIT_REPO/openquakeplatform/dump/base_topiccategory.json

## populate geoserver data infrastructure
cd ~/oq-platform2
$HOME/$GIT_REPO/openquakeplatform/bin/oq-gs-builder.sh populate "openquakeplatform/" "openquakeplatform/" "openquakeplatform/bin" "oqplatform" "oqplatform" "$GEO_DBNAME" "$GEO_DBUSER" "$GEO_DBPWD" "geoserver/data" isc_viewer ghec_viewer
# 
# ## Update layers from Geoserver to geonode
cd ~/geonode
python manage.py makemigrations
python manage.py migrate
python manage.py updatelayers -u GEM

cd $HOME/
$GIT_REPO/openquakeplatform/bin/oq-gs-builder.sh drop
$GIT_REPO/openquakeplatform/bin/oq-gs-builder.sh restore ~/oq-platform2/gs_data/output geonode_dev geonode_dev geonode_dev

## Add old documents
# mkdir $HOME/geonode/geonode/uploaded/documents/
cd ~/geonode
python ./manage.py add_documents
cp -r $HOME/oq-platform2/openquakeplatform/common/gs_data/documents $HOME/geonode/geonode/uploaded/

# Create programmatically ISC and GHEC json
python manage.py create_iscmap $HOME/$GIT_REPO/openquakeplatform/isc_viewer/dev_data/isc_map_comps.json
python manage.py create_ghecmap $HOME/$GIT_REPO/openquakeplatform/ghec_viewer/dev_data/ghec_map_comps.json

cd ~/ 
if [ "$NO_EXEC_TEST" != "notest" ] ; then
    exec_test
fi

if [ "$GEM_TEST_LATEST" = "true" ]; then
    # pip freeze > ~/latest_requirements.txt
    $HOME/$GIT_REPO/create_gem_requirements.sh > gem_geonode_requirements.txt  
    cd ~/geonode
    git log -1 > ~/latest_geonode_commit.txt
    cd -
fi

## Stop Geonode
cd ~/geonode

paver -f $HOME/$GIT_REPO/pavement.py stop
 
# python manage.py migrate account --noinput
# paver -f $HOME/$GIT_REPO/pavement.py sync
# paver -f $HOME/$GIT_REPO/pavement.py start -b 0.0.0.0:8000
# 
# python ./manage.py updatelayers
# 
# sudo supervisorctl stop openquake-webui
# paver -f $HOME/$GIT_REPO/pavement.py stop
