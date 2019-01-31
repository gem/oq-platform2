#!/bin/bash                                                                     
# Copyright (c) 2013-2019, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake.  If not, see <http://www.gnu.org/licenses/>.

# if [ $GEM_SET_DEBUG ]; then
    set -x
# fi
set -e

if [ -f /etc/openquake/platform/local_settings.py ]; then
    GEM_IS_INSTALL=n
else
    GEM_IS_INSTALL=y
fi

sudo apt-get update
sudo apt install -y git python-virtualenv wget

# if [ "$GEM_IS_INSTALL" == "y" ]; then
    # delete all folder used
    sudo rm -rf env oq-platform2 geonode oq-platform-taxtweb oq-platform-building-class oq-platform-ipt oq-platform-data
    
    # if exists, delete postgres:
    sudo apt-get --purge remove -y postgresql postgresql-9.5 postgresql-9.5-postgis-2.2 postgresql-9.5-postgis-scripts postgresql-client-9.5 postgresql-client-common postgresql-common postgresql-contrib-9.5
# fi
# Create and source virtual env
virtualenv env
source $HOME/env/bin/activate

sudo apt install -y python-dev libpq-dev libgdal-dev openjdk-8-jdk-headless

sudo apt-get install -y postgresql-9.5-postgis-2.2 postgresql-9.5-postgis-scripts curl xmlstarlet supervisor
pip install numpy
sudo apt install -y apache2 tomcat7
python -m pip install "django<2"
pip install django-nested-inline
pip install django_extras
pip install -e git+git://github.com/gem/django-chained-selectbox.git@pla26#egg=django-chained-selectbox-0.2.2
pip install -e git+git://github.com/gem/django-nested-inlines.git@pla26#egg=django-nested-inlines-0.1.4
pip install -e git+git://github.com/gem/django-chained-multi-checkboxes.git@pla26#egg=django-chained-multi-checkboxes-0.4.1
pip install -e git+git://github.com/gem/wadofstuff-django-serializers.git@pla26#egg=wadofstuff-django-serializers-1.1.2
pip install scipy


# install engine
sudo apt-get install -y software-properties-common
# sudo add-apt-repository -y ppa:openquake-automatic-team/latest-master
sudo add-apt-repository -y ppa:openquake/release-3.1
sudo apt-get update
sudo apt-get install -y --force-yes python-oq-engine

LXC_IP="$1"
GIT_BRANCH="$2"
GIT_GEO_REPO="2.6.x"
GEO_STABLE_HASH="aa5932d"
GIT_REPO="oq-platform2"
GEO_DBUSER="geonode"
GEM_GIT_REPO="git://github.com/gem"
NO_EXEC_TEST="$3"

# create secret key
function key_create () {
    python -c "import string ; import random
def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))
print id_generator()"
}
SECRET="$(key_create)"

# create db pwd
function passwd_create () {
    python -c "import string ; import random
def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))
print id_generator()"
}
gem_db_pass="$(passwd_create)"

function setup_postgres_once() {

sudo -u postgres createdb $GEO_DBUSER
sudo -u postgres createdb $GEO_DBUSER-imports

cat << EOF | sudo -u postgres psql
    CREATE USER "geonode" WITH PASSWORD '$gem_db_pass';
    GRANT ALL PRIVILEGES ON DATABASE "$GEO_DBUSER" to geonode;
    GRANT ALL PRIVILEGES ON DATABASE "$GEO_DBUSER-imports" to geonode;
EOF

sudo -u postgres psql -d $GEO_DBUSER -c 'CREATE EXTENSION postgis;'
sudo -u postgres psql -d $GEO_DBUSER -c 'GRANT ALL ON geometry_columns TO PUBLIC;'
sudo -u postgres psql -d $GEO_DBUSER -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;'

sudo -u postgres psql -d $GEO_DBUSER-imports -c 'CREATE EXTENSION postgis;'
sudo -u postgres psql -d $GEO_DBUSER-imports -c 'GRANT ALL ON geometry_columns TO PUBLIC;'
sudo -u postgres psql -d $GEO_DBUSER-imports -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;'

# add unaccent extension and icompare_unaccent function into postgres
cat << EOF | sudo -u postgres psql -d geonode                                                                                                                                                                                         
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
sudo sed -i '1 s@^@local  all             '"$GEO_DBUSER"'             md5\n@g' /etc/postgresql/9.5/main/pg_hba.conf
sudo sed -i '2 s@^@host  all    '"$GEO_DBUSER"'         '"$LXC_IP"'/32             md5\n@g' /etc/postgresql/9.5/main/pg_hba.conf
# sudo sed -i '2 s@^@host  all    '"$GEO_DBUSER"'         '"$LXC_IP"'             md5\n@g' /etc/postgresql/9.5/main/pg_hba.conf
sudo sed -i "1 s@^@listen_addresses = '127.0.0.1,localhost,"$LXC_IP"'\n@g" /etc/postgresql/9.5/main/postgresql.conf

#restart postgres
sudo service postgresql restart
}

function clone_platform() {
    # clone oq-platform2
    cd $HOME
    git clone https://github.com/gem/oq-platform2.git
    cd oq-platform2
    git checkout oqstyle
    pip install -e .
}

function oq_application() {
    # clone ipt, taxtweb, building-classification-survey
    cd $HOME
    for repo in oq-platform-taxtweb oq-platform-ipt oq-platform-building-class oq-platform-data; do
        # for repo in oq-platform-taxtweb; do
        if [ "$GIT_BRANCH" = "master" ]; then false ; else git clone -b "$GIT_BRANCH" https://github.com/gem/${repo}.git ; fi || git clone -b oq-platform2 https://github.com/gem/${repo}.git || git clone https://github.com/gem/${repo}.git
        if [ "${repo}" != "oq-platform-data" ]; then
            cd ${repo}
            pip install -e .
            cd $HOME
        fi
    done
}

function install_geonode() { 
    # clone geonode
    cd $HOME
    git clone --depth=1 -b "$GIT_GEO_REPO" https://github.com/GeoNode/geonode.git

    # download Geonode zip
    wget http://ftp.openquake.org/oq-platform2/GeoNode-2.6.x.zip
    
    # override dev-config yml into the Geonode
    cd $HOME/geonode
    git checkout dev_config.yml
    patch < $HOME/$GIT_REPO/openquakeplatform/bin/dev_config_yml.patch
    
    # install geonode
    git checkout "$GEO_STABLE_HASH"
    pip install -r requirements.txt
    pip install -r $HOME/$GIT_REPO/gem_geonode_requirements.txt
    pip install -e .
    
    sudo apt install -y python-gdal gdal-bin
    
    # copy Geonode zip and oq_install script in package folder of Geonode
    cd $HOME/geonode/package/
    sudo cp -r $HOME/GeoNode-2.6.x.zip .
    sudo cp $HOME/oq_install.sh . 
    
    # install Geonode
    cd ..
    sudo ./package/oq_install.sh -s pre ~/oq-platform2/openquakeplatform/common/geonode_install_pre.sh
    
    # enable wsgi apache
    sudo apt-get install libapache2-mod-wsgi
    sudo a2enmod wsgi
    sudo invoke-rc.d apache2 restart
    
    # Create local_settings with pavement from repo
    paver -f $HOME/oq-platform2/pavement.py oqsetup -l $LXC_IP -u localhost:8800 -s $HOME/geonode/data -d geonode -p $gem_db_pass -x $LXC_IP -g localhost:8080 -k $SECRET
    sudo mv /etc/geonode/local_settings.py /etc/geonode/geonode_local_settings.py                                                                                                                                    
    sudo cp  $HOME/oq-platform2/local_settings.py /etc/geonode/
    sudo ./package/oq_install.sh -s post $HOME/oq-platform2/openquakeplatform/common/geonode_install_post.sh
    sudo ./package/oq_install.sh -s setup_geoserver $HOME/oq-platform2/openquakeplatform/common/geonode_install_pre.sh
    
    sudo sed -i '1 s@^@WSGIPythonHome '"$HOME"'/env\n@g' /etc/apache2/sites-enabled/geonode.conf
    sudo invoke-rc.d apache2 restart                      
}

function apply_data() {
    cd $HOME
    geonode syncdb  
    geonode migrate
    geonode vuln_groups_create
    geonode add_user $HOME/oq-private/old_platform_documents/json/auth_user.json
    geonode loaddata $HOME/$GIT_REPO/openquakeplatform/dump/base_topiccategory.json
    geonode import_vuln_geo_applicability_csv $HOME/$GIT_REPO/openquakeplatform/vulnerability/dev_data/vuln_geo_applicability_data.csv
    geonode loaddata $HOME/$GIT_REPO/openquakeplatform/vulnerability/post_fixtures/initial_data.json
    geonode loaddata -v 3 --app vulnerability $HOME/oq-private/old_platform_documents/json/all_vulnerability.json
    geonode create_gem_user
    pip install simplejson==2.0.9
    # export CATALINA_OPTS="-Xms4096M -Xmx4096M"
    sudo sed -i 's/-Xmx128m/-Xmx4096m/g' /etc/default/tomcat7
    sudo service tomcat7 restart
    
    cd $HOME/oq-platform2
    $HOME/oq-platform2/openquakeplatform/bin/oq-gs-builder.sh populate -a $HOME/oq-private/old_platform_documents/output "openquakeplatform/" "openquakeplatform/" "openquakeplatform/bin" "oqplatform" "oqplatform" "geonode" "geonode" "$gem_db_pass" "/var/lib/tomcat7/webapps/geoserver/data"
    
    cd ~/
    # Put sql for all layers
    for lay in $(cat $HOME/oq-private/old_platform_documents/sql_layers/in/layers_list.txt); do
        sudo -u postgres psql -d $GEO_DBUSER -c '\copy '$lay' FROM '$HOME/oq-private/old_platform_documents/sql_layers/out/$lay''
    done
    
    sudo cp -r $HOME/oq-private/old_platform_documents/thumbs/ $HOME/env/lib/python2.7/site-packages/geonode/uploaded/
    sudo chmod 777 -R $HOME/env/lib/python2.7/site-packages/geonode/uploaded/thumbs
    sudo cp -r $HOME/$GIT_REPO/openquakeplatform/common/gs_data/documents $HOME/env/lib/python2.7/site-packages/geonode/uploaded/
    geonode add_documents_prod
    # geonode updatelayers
    # geonode sync_geofence

    sudo invoke-rc.d apache2 restart
    sudo service tomcat7 restart
}

function svir_world_data() {
    sudo sed -i 's/:8000//g' $HOME/env/local/lib/python2.7/site-packages/geonode/static_root/irv/js/irv_viewer.js
    geonode collectstatic --noinput --verbosity 0 
    geonode migrate
    geonode loaddata oq-platform-data/api/data/world_prod.json.bz2 
    geonode loaddata oq-platform-data/api/data/svir_prod.json.bz2
}

#function complete procedure for tests
function initialize_test() {
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
    cp $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py.tmpl $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py
    cp $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py.tmpl oq-platform2/openquakeplatform/set_thumb/moon_config.py

    sudo sed -i 's/localhost:8000/localhost/g' $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py
    sudo sed -i 's/localhost:8000/localhost/g' $HOME/$GIT_REPO/openquakeplatform/set_thumb/moon_config.py

    # cd $GIT_REPO
    export PYTHONPATH=$HOME/oq-moon:$HOME/$GIT_REPO:$HOME/$GIT_REPO/openquakeplatform/test/config:$HOME/oq-platform-taxtweb:$HOME/oq-platform-ipt:$HOME/oq-platform-building-class
}

function exec_set_map_thumbs() {
    export DISPLAY=:1
    python -m openquake.moon.nose_runner --failurecatcher dev -s -v --with-xunit --xunit-file=xunit-platform-dev.xml $GIT_REPO/openquakeplatform/set_thumb/mapthumbnail_test.py
}

function oq_install() {
    setup_postgres_once
    clone_platform
    oq_application
    install_geonode
    apply_data
    svir_world_data
    if [ "$NO_EXEC_TEST" != "notest" ] ; then
        initialize_test
        exec_set_map_thumbs
    fi    
}

oq_install
