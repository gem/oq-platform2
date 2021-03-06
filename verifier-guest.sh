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
sudo systemctl stop tomcat7
sudo systemctl stop apache2

set -o errtrace

#display each command before executing it
. .gem_init.sh

REINSTALL=
if [ "$1"  = "-r" -o "$1" = "--reinstall" ]; then
    REINSTALL=true
    shift
fi
GIT_BRANCH="$1"
GIT_GEO_BRANCH="$2"
GIT_REPO="$3"
export LXC_IP="$4"
NO_EXEC_TEST="$5"
GEO_DBNAME="geonode_dev"
GEO_DBUSER="geonode_dev"
GEO_DBPWD="geonode_dev"
plugins_branch_id="$6"

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
    pip install -e git+git://github.com/gem/django-chained-selectbox.git#egg=django-chained-selectbox
    pip install -e git+git://github.com/gem/django-nested-inlines.git#egg=django-nested-inlines
    pip install -e git+git://github.com/gem/django-chained-multi-checkboxes.git#egg=django-chained-multi-checkboxes
    pip install -e git+git://github.com/gem/wadofstuff-django-serializers.git#egg=wadofstuff-django-serializers
    pip install django-request==1.5.2
}

#function complete procedure for tests
initialize_test () {
    #install selenium,pip,geckodriver,clone oq-moon and execute tests with nose
    # sudo apt-get -y install python-pip wget
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
        git clone -b "$GIT_BRANCH" "$GEM_GIT_REPO/oq-moon.git" || git clone "$GEM_GIT_REPO/oq-moon.git"
    fi
    cp $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py.tmpl $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py

    # cd $GIT_REPO
    export PYTHONPATH=$HOME/oq-moon:$HOME/$GIT_REPO:$HOME/$GIT_REPO/openquakeplatform/test/config:$HOME/oq-platform-taxtweb:$HOME/oq-platform-ipt:$HOME/oq-platform-building-class
}

exec_test () {
    sed -i 's/TIME_INVARIANT_OUTPUTS = False/TIME_INVARIANT_OUTPUTS = True/g' $GIT_REPO/local_settings.py
    export GEM_OPT_PACKAGES="$(python -c 'from openquakeplatform.settings import STANDALONE_APPS ; print(",".join(x for x in STANDALONE_APPS))')"
    export GEM_PLA_ADMIN_ID=1000
    export DISPLAY=:1
    python -m openquake.moon.nose_runner --failurecatcher dev -s -v --with-xunit --xunit-file=xunit-platform-dev.xml $GIT_REPO/openquakeplatform/test # || true
}

exec_set_map_thumbs () {
    export DISPLAY=:1
    python -m openquake.moon.nose_runner --failurecatcher dev -s -v --with-xunit --xunit-file=xunit-platform-dev.xml $GIT_REPO/openquakeplatform/set_thumb/mapthumbnail_test.py
}

migrations_vulnerability_test() {
    pushd ~/geonode
    python manage.py test -v 3 $HOME/$GIT_REPO/openquakeplatform/migrations_test.py
    popd
}

updatelayer() {
    cd ~/geonode
    python manage.py updatelayers
}

rem_sig_hand() {
    trap "" ERR
    echo 'signal trapped'
    set +e
    sudo systemctl stop openquake-webui.service

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


# sudo apt update
# sudo apt install -y git python-dev python-virtualenv libpq-dev libgdal-dev zip unzip

# install last version of jdk 1-8-0_265 and downgrade to 1.8.0.242 used from Geoserver
function install_jdk() {
   # sudo apt install -y openjdk-8-jdk-headless
   test -d /usr/lib/jvm/ || sudo mkdir -p /usr/lib/jvm/ 
   cd /usr/lib/jvm/
   sudo mv java-8-openjdk-amd64 java-8-openjdk-amd64.last || true
   sudo wget http://ftp.openquake.org/oq-platform2/8u242.tgz
   sudo tar zxvf 8u242.tgz
   sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-8-openjdk-amd64/bin/java 1
}

install_jdk

# Used a local clone (see verifier.sh)
# git clone -b "$GIT_BRANCH" https://github.com/gem/oq-platform2.git

# if reinstall try to turn off all running daemon
if [ "$REINSTALL" ]; then
    if [ -f ~/env/bin/activate -a -f ~/oq-platform2/pavement.py -a -d ~/geonode ]; then
        . ~/env/bin/activate
        cd ~/geonode
        sudo systemctl stop openquake-webui.service
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

cd ~

# install demos from engine trevis build
rm -f demos-*.zip
wget https://artifacts.openquake.org/travis/demos-${plugins_branch_id}.zip || wget https://artifacts.openquake.org/travis/demos-master.zip
rm -rf demos
unzip demos-*.zip

#install and configuration postgres
# sudo apt-get install -y postgresql-9.5-postgis-2.2 postgresql-9.5-postgis-scripts curl xmlstarlet supervisor
if [ "$REINSTALL" ]; then
    sudo -u postgres dropdb geonode_dev
    sudo -u postgres dropdb geonode_dev-imports
    sudo -u postgres dropuser "$GEO_DBUSER"
fi
sudo -u postgres createdb geonode_dev
sudo -u postgres createdb geonode_dev-imports

cat << EOF | sudo -u postgres psql
    CREATE USER "$GEO_DBUSER" WITH PASSWORD '$GEO_DBPWD';
    GRANT ALL PRIVILEGES ON DATABASE "$GEO_DBNAME" to $GEO_DBUSER;
    GRANT ALL PRIVILEGES ON DATABASE "geonode_dev-imports" to $GEO_DBUSER;
    ALTER USER "$GEO_DBUSER" CREATEDB;
    ALTER ROLE "$GEO_DBUSER" SUPERUSER;
EOF

sudo -u postgres psql -d geonode_dev -c 'CREATE EXTENSION postgis;'
sudo -u postgres psql -d geonode_dev -c 'GRANT ALL ON geometry_columns TO PUBLIC;'
sudo -u postgres psql -d geonode_dev -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;'

sudo -u postgres psql -d geonode_dev-imports -c 'CREATE EXTENSION postgis;'
sudo -u postgres psql -d geonode_dev-imports -c 'GRANT ALL ON geometry_columns TO PUBLIC;'
sudo -u postgres psql -d geonode_dev-imports -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;'

# add unaccent extension and icompare_unaccent function into postgres
cat << EOF | sudo -u postgres psql -d geonode_dev

    -- NOTE: originally deployed as migration, we realized that this sql script must
    --       be executed for every new installation (devel or production).
    --       The script is idempotent so we decided to keep the original migration script too
    
    DROP OPERATOR IF EXISTS =~@ (character varying, character varying);
    DROP FUNCTION IF EXISTS icompare_unaccent(character varying, character varying);
    DROP EXTENSION IF EXISTS unaccent;
    
    CREATE EXTENSION unaccent;
    CREATE FUNCTION icompare_unaccent(character varying, character varying) RETURNS boolean
        AS 'SELECT upper(unaccent(\$1)) LIKE upper(unaccent(\$2));'
        LANGUAGE SQL
        IMMUTABLE
        RETURNS NULL ON NULL INPUT;
    
    CREATE OPERATOR =~@ (
        LEFTARG = character varying,
        RIGHTARG = character varying,
        PROCEDURE = icompare_unaccent,
        NEGATOR = !=~@
    );
EOF

#insert line in pg_hba.conf postgres
if ! sudo head -n 1 /etc/postgresql/9.5/main/pg_hba.conf | grep -q "local \+all \+$GEO_DBUSER \+md5"; then
    sudo sed -i '1 s@^@local  all             '"$GEO_DBUSER"'             md5\n@g' /etc/postgresql/9.5/main/pg_hba.conf
fi
#restart postgres
sudo service postgresql restart

#install setuptools specitic version for python 2.7
pip install "setuptools==44.0.0"

#install numpy
pip install "numpy>=1.16,<1.17"

#install numpy
pip install "django-cors-headers>=2.4.1,<2.5.0"

## Clone GeoNode
if [ -z "$REINSTALL" ]; then
    git clone -b "$GIT_GEO_BRANCH" https://github.com/gem/geonode.git
else
    cd geonode
    git clean -dfx
    git checkout "$GIT_GEO_BRANCH"
    cd -
fi

# install engine
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:openquake/ppa
# sudo add-apt-repository -y ppa:openquake-automatic-team/latest-master
sudo apt-get update
sudo apt-get install -y --force-yes python3-oq-engine python3-oq-libs-extra

## Install GeoNode and dependencies
cd $HOME/geonode
pip install -r requirements.txt

if [ "$GEM_TEST_LATEST" != "true" ]; then
    ## more stable dependencies installed
    pip install -r $HOME/$GIT_REPO/gem_geonode_requirements.txt
fi

pip install configparser
pip install -e .

# Install the system python-gdal
# sudo apt-get install -y python-gdal

cd ~
# Create a symbolic link in your virtualenv
ln -sf /usr/lib/python2.7/dist-packages/osgeo env/lib/python2.7/site-packages/osgeo

## clone and setting pythonpath taxtweb, ipt, oq-platform2
cd ~

if [ -z "$REINSTALL" ]; then
    for repo in oq-platform-taxtweb oq-platform-ipt oq-platform-building-class; do
        # for repo in oq-platform-taxtweb; do
        if [ "$plugins_branch_id" != 'master' ]; then
            GIT_BRANCH="$plugins_branch_id"
        fi
        if [ "$GIT_BRANCH" = "master" ]; then false ; else git clone -b "$GIT_BRANCH" https://github.com/gem/${repo}.git ; fi || git clone https://github.com/gem/${repo}.git
    done
fi

## Setup environment
geonode_setup_env

## Sync and setup GeoNode
cd ~/geonode

# override dev-config yml into the Geonode
if [ "$REINSTALL" ]; then
    git checkout dev_config.yml
fi

patch < $HOME/$GIT_REPO/openquakeplatform/bin/dev_config_yml.patch

paver -f $HOME/$GIT_REPO/pavement.py setup

## Create local_settings with pavement from repo
paver -f $HOME/$GIT_REPO/pavement.py oqsetup -l $LXC_IP:8000 -u localhost:8800 -s $HOME/geonode/data -d geonode_dev -p geonode_dev -x $LXC_IP:8080 -g localhost:8080 -k secret_key

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

## load data for svir
python manage.py loaddata $HOME/$GIT_REPO/openquakeplatform/world/dev_data/world.json.bz2
python manage.py loaddata $HOME/$GIT_REPO/openquakeplatform/svir/dev_data/svir.json.bz2

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
$HOME/$GIT_REPO/openquakeplatform/bin/oq-gs-builder.sh populate -a $HOME/$GIT_REPO/gs_data/output "openquakeplatform/" "openquakeplatform/" "openquakeplatform/bin" "oqplatform" "oqplatform" "$GEO_DBNAME" "$GEO_DBUSER" "$GEO_DBPWD" "geoserver/data" isc_viewer ghec_viewer

#
## Add old documents
cd ~/geonode
mkdir -p $HOME/geonode/geonode/uploaded/
cp -r $HOME/$GIT_REPO/openquakeplatform/common/gs_data/documents $HOME/geonode/geonode/uploaded/
python ./manage.py add_documents

cd ~/
# install geckodriver and selenium
initialize_test
# Set thumbnails all maps
exec_set_map_thumbs

## Update layers from Geoserver to geonode
cd ~/geonode
python manage.py makemigrations
python manage.py migrate
python manage.py updatelayers -u GEM

# Create programmatically ISC and GHEC json
python manage.py create_iscmap $HOME/$GIT_REPO/openquakeplatform/isc_viewer/dev_data/isc_map_comps.json
python manage.py create_ghecmap $HOME/$GIT_REPO/openquakeplatform/ghec_viewer/dev_data/ghec_map_comps.json

# Import vulnerability curves
python manage.py loaddata -v 3 --app vulnerability $HOME/$GIT_REPO/openquakeplatform/common/gs_data/dump/all_vulnerability.json

cd ~/
# sql qgis_irmt_053d2f0b_5753_415b_8546_021405e615ec layer
sudo -u postgres psql -d geonode_dev -c '\copy qgis_irmt_053d2f0b_5753_415b_8546_021405e615ec FROM '$HOME/$GIT_REPO/gs_data/output/sql/qgis_irmt_053d2f0b_5753_415b_8546_021405e615ec.sql''

# sql assumpcao2014 layer
sudo -u postgres psql -d geonode_dev -c '\copy assumpcao2014 FROM '$HOME/$GIT_REPO/gs_data/output/sql/assumpcao2014.sql''

updatelayer

# test vulnerability migrations
migrations_vulnerability_test

cd ~/

if [ "$NO_EXEC_TEST" != "notest" ] ; then
    sed -i 's/TIME_INVARIANT_OUTPUTS = False/TIME_INVARIANT_OUTPUTS = True/g' $HOME/$GIT_REPO/local_settings.py
    exec_test
fi

if [ "$GEM_TEST_LATEST" = "true" ]; then
    # pip freeze > ~/latest_requirements.txt
    $HOME/$GIT_REPO/create_gem_requirements.sh > gem_geonode_requirements.txt
    pushd ~/geonode
    git log -1 > ~/latest_geonode_commit.txt
    popd
fi

cd ~/geonode

# Stop Geonode
sudo systemctl stop openquake-webui.service
paver -f $HOME/$GIT_REPO/pavement.py stop
