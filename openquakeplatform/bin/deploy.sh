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

GIT_REPO="oq-platform2"

# delete all folder used
sudo rm -rf env $GIT_REPO geonode oq-platform-taxtweb oq-platform-building-class oq-platform-ipt oq-platform-data /var/www/geonode /etc/geonode /var/lib/tomcat7/webapps GeoNode-2.6.x.zip* 

# if exists, delete postgres:
sudo apt-get --purge remove -y postgresql postgresql-9.5 postgresql-9.5-postgis-2.2 postgresql-9.5-postgis-scripts postgresql-client-9.5 postgresql-client-common postgresql-common postgresql-contrib-9.5 tomcat7

sudo a2dissite geonode || true 
sudo rm /etc/apache2/sites-available/geonode.conf || true
sudo rm /etc/apache2/sites-enabled/geonode.conf || true
sudo rm /etc/geonode/local_settings.py || true
sudo service apache2 restart || true

sudo apt-get update
sudo apt install -y git python-virtualenv wget

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
pip install git+git://github.com/gem/django-chained-selectbox.git@pla26#egg=django-chained-selectbox-0.2.2
pip install git+git://github.com/gem/django-nested-inlines.git@pla26#egg=django-nested-inlines-0.1.4
pip install git+git://github.com/gem/django-chained-multi-checkboxes.git@pla26#egg=django-chained-multi-checkboxes-0.4.1
pip install git+git://github.com/gem/wadofstuff-django-serializers.git@pla26#egg=wadofstuff-django-serializers-1.1.2


# install engine
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:openquake/ppa
sudo apt-get update
sudo apt-get install -y --force-yes python3-oq-engine

# check if are dev/prod data installation
if [ "$1" = "-d" ]; then
    export DEVEL_DATA=y
    shift
fi

export LXC_IP="$1"
GIT_BRANCH="$2"
GIT_GEO_REPO="2.6.x"
GEO_STABLE_HASH="aa5932d"
GEO_DBUSER="geonode"
GEM_GIT_REPO="git://github.com/gem"
NO_EXEC_TEST="$3"
export PROD_INSTALL='y'
export DATA_PROD="$4"

# branch for ipt, taxtweb, classification survey
GIT_BRANCH_APP="$4"
if ["$GIT_BRANCH_APP" = '']; then
    GIT_BRANCH_APP="master"
fi

# sudo usermod -aG www-data $USER

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

function apache_tomcat_restart() {
   sudo service apache2 restart
   sudo service tomcat7 restart
   sleep 220
   echo "restart Apache/Tomcat"
}

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

    sudo sed -i "1 s@^@listen_addresses = '127.0.0.1,localhost,"$LXC_IP"'\n@g" /etc/postgresql/9.5/main/postgresql.conf
    
    # restart postgres
    sudo service postgresql restart
}

function clone_platform() {
    # clone oq-platform
    cd $HOME
    git clone https://github.com/gem/oq-platform2.git
    cd $GIT_REPO
    git checkout $GIT_BRANCH
    if [ "$DEVEL_DATA" ]; then
         ## for exposure fake data
         sed -i "2 s@^@#the line below was added by deploy.sh in DEVEL mode\nrecursive-include openquakeplatform/exposure/fake_data/      *\n@g" MANIFEST.in
    fi
    pip install .
}

function oq_application() {
    # clone ipt, taxtweb, building-classification-survey
    cd $HOME
    for repo in oq-platform-taxtweb oq-platform-ipt oq-platform-building-class oq-platform-data; do
        # for repo in oq-platform-taxtweb; do
        if [ "$GIT_BRANCH_APP" = "master" ]; then false ; else git clone -b "$GIT_BRANCH_APP" https://github.com/gem/${repo}.git ; fi || git clone -b $GIT_REPO https://github.com/gem/${repo}.git || git clone https://github.com/gem/${repo}.git
        if [ "${repo}" != "oq-platform-data" ]; then
            pushd ${repo}
            pip install .
            popd
        fi
    done
}

function install_geonode() { 
    # clone geonode
    cd $HOME
    git clone --depth=1 -b "$GIT_GEO_REPO" https://github.com/GeoNode/geonode.git

    # download Geonode zip
    wget http://ftp.openquake.org/$GIT_REPO/GeoNode-2.6.x.zip
    
    # override dev-config yml into the Geonode
    cd $HOME/geonode
    git checkout dev_config.yml
    patch < $HOME/$GIT_REPO/openquakeplatform/bin/dev_config_yml.patch
    
    # install geonode
    git checkout "$GEO_STABLE_HASH"
    pip install -r requirements.txt
    pip install -r $HOME/$GIT_REPO/gem_geonode_requirements.txt
    pip install .
    
    #TODO check python-gdal deps
    sudo apt install -y python-gdal gdal-bin
    
    # copy Geonode zip and oq_install script in package folder of Geonode
    cd $HOME/geonode/package/
    cp -r $HOME/GeoNode-2.6.x.zip .
    cp $HOME/oq_install.sh .
    
    # install Geonode
    cd ..
    sudo -E ./package/oq_install.sh -s pre $HOME/$GIT_REPO/openquakeplatform/common/geonode_install.sh
    
    # enable wsgi apache
    sudo apt-get install libapache2-mod-wsgi
    sudo a2enmod wsgi
    sudo service apache2 restart
    
    # Create local_settings with pavement from repo
    paver -f $HOME/$GIT_REPO/pavement.py oqsetup -l $LXC_IP -u localhost:8800 -s /var/www/geonode/data -d geonode -p $gem_db_pass -x $LXC_IP -g localhost:8080 -k $SECRET
    sudo rm /etc/geonode/local_settings.py
    sudo cp  $HOME/$GIT_REPO/local_settings.py /etc/geonode/
    
    sudo sed -i "24 s@^@MEDIA_ROOT = '/var/www/geonode/uploaded'\n@g" /etc/geonode/local_settings.py
    sudo sed -i "25 s@^@STATIC_ROOT = '/var/www/geonode/static'\n@g" /etc/geonode/local_settings.py

    # pre and post install platform
    sudo -E ./package/oq_install.sh -s post $HOME/$GIT_REPO/openquakeplatform/common/geonode_install.sh
    sudo -E ./package/oq_install.sh -s setup_geoserver $HOME/$GIT_REPO/openquakeplatform/common/geonode_install.sh
    
    sudo sed -i '1 s@^@WSGIPythonHome '"$HOME"'/env\n@g' /etc/apache2/sites-enabled/geonode.conf
    sudo service apache2 restart                      
}

function apply_data() {
    cd $HOME
    geonode syncdb  
    geonode migrate
    geonode loaddata $HOME/$GIT_REPO/openquakeplatform/dump/base_topiccategory.json
    geonode import_vuln_geo_applicability_csv $HOME/$GIT_REPO/openquakeplatform/vulnerability/dev_data/vuln_geo_applicability_data.csv
    geonode vuln_groups_create

    if [ "$DEVEL_DATA" ]; then
        geonode add_user $HOME/$GIT_REPO/openquakeplatform/common/gs_data/dump/auth_user.json
        geonode loaddata $HOME/$GIT_REPO/openquakeplatform/common/gs_data/dump/base_region.json
        geonode loaddata -v 3 --app vulnerability $HOME/$GIT_REPO/openquakeplatform/common/gs_data/dump/all_vulnerability.json
        geonode create_gem_user
    else
        geonode add_user $HOME/oq-private/old_platform_documents/json/auth_user.json
        geonode loaddata $HOME/oq-private/old_platform_documents/json/base_region.json
        geonode loaddata $HOME/$GIT_REPO/openquakeplatform/vulnerability/post_fixtures/initial_data.json
        geonode loaddata -v 3 --app vulnerability $HOME/oq-private/old_platform_documents/json/all_vulnerability.json
        geonode create_gem_user
    fi    
    pip install simplejson==2.0.9
    sudo sed -i 's/-Xmx128m/-Xmx4096m/g' /etc/default/tomcat7
    sudo service tomcat7 restart
    
    if [ -z "$DEVEL_DATA" ]; then
        cp -r $HOME/oq-private/old_platform_documents/thumbs/ /var/www/geonode/uploaded/
    fi

    cp -r $HOME/$GIT_REPO/openquakeplatform/common/gs_data/documents /var/www/geonode/uploaded/

    cd $HOME/$GIT_REPO
    if [ "$DEVEL_DATA" ]; then

         ## load data for gec and isc viewer
         geonode import_isccsv $HOME/$GIT_REPO/openquakeplatform/isc_viewer/dev_data/isc_data.csv  $HOME/$GIT_REPO/openquakeplatform/isc_viewer/dev_data/isc_data_app.csv
         geonode import_gheccsv $HOME/$GIT_REPO/openquakeplatform/ghec_viewer/dev_data/ghec_data.csv

         # Create programmatically ISC and GHEC json
         geonode create_iscmap $HOME/$GIT_REPO/openquakeplatform/isc_viewer/dev_data/isc_map_comps.json
         geonode create_ghecmap $HOME/$GIT_REPO/openquakeplatform/ghec_viewer/dev_data/ghec_map_comps.json

         apache_tomcat_restart

         $HOME/$GIT_REPO/openquakeplatform/bin/oq-gs-builder.sh populate -a $HOME/$GIT_REPO/gs_data/output "openquakeplatform/" "openquakeplatform/" "openquakeplatform/bin" "oqplatform" "oqplatform" "geonode" "geonode" "$gem_db_pass" "/var/lib/tomcat7/webapps/geoserver/data" isc_viewer ghec_viewer
    else    
         $HOME/$GIT_REPO/openquakeplatform/bin/oq-gs-builder.sh populate -a $HOME/oq-private/old_platform_documents/output "openquakeplatform/" "openquakeplatform/" "openquakeplatform/bin" "oqplatform" "oqplatform" "geonode" "geonode" "$gem_db_pass" "/var/lib/tomcat7/webapps/geoserver/data"
    fi

    cd $HOME/

     if [ "$DEVEL_DATA" ]; then
         # sql qgis_irmt_053d2f0b_5753_415b_8546_021405e615ec layer
         sudo -u postgres psql -d geonode -c '\copy qgis_irmt_053d2f0b_5753_415b_8546_021405e615ec FROM '$HOME/$GIT_REPO/gs_data/output/sql/qgis_irmt_053d2f0b_5753_415b_8546_021405e615ec.sql''
         
         # sql assumpcao2014 layer
         sudo -u postgres psql -d geonode -c '\copy assumpcao2014 FROM '$HOME/$GIT_REPO/gs_data/output/sql/assumpcao2014.sql''
         geonode updatelayers
         geonode add_documents
     else
         # Put sql for all layers
         for lay in $(cat $HOME/oq-private/old_platform_documents/sql_layers/in/layers_list.txt); do
             sudo -u postgres psql -d $GEO_DBUSER -c '\copy '$lay' FROM '$HOME/oq-private/old_platform_documents/sql_layers/out/$lay''
         done
         geonode add_documents_prod
     fi
     # fix name and sitedomain in db
     geonode fixsitename
}

function svir_world_data() {
    geonode migrate
    if [ "$DEVEL_DATA" ]; then
        geonode loaddata $HOME/$GIT_REPO/openquakeplatform/world/dev_data/world.json.bz2
        geonode loaddata $HOME/$GIT_REPO/openquakeplatform/svir/dev_data/svir.json.bz2
    else    
        sed -i 's/:8000//g' /var/www/geonode/static/irv/js/irv_viewer.js
        geonode collectstatic --noinput --verbosity 0 
        geonode loaddata oq-platform-data/api/data/world_prod.json.bz2 
        geonode loaddata oq-platform-data/api/data/svir_prod.json.bz2
    fi    
}

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
        git clone -b "$GIT_BRANCH" "$GEM_GIT_REPO/oq-moon.git" || git clone -b $GIT_REPO "$GEM_GIT_REPO/oq-moon.git" || git clone "$GEM_GIT_REPO/oq-moon.git"
    fi
    cp $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py.tmpl $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py
    cp $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py.tmpl $GIT_REPO/openquakeplatform/set_thumb/moon_config.py

    sed -i 's/localhost:8000/'"$LXC_IP"'/g' $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py
    sed -i 's/localhost:8000/'"$LXC_IP"'/g' $HOME/$GIT_REPO/openquakeplatform/set_thumb/moon_config.py

    export PYTHONPATH=$HOME/oq-moon:$HOME/$GIT_REPO:$HOME/$GIT_REPO/openquakeplatform/test/config:$HOME/oq-platform-taxtweb:$HOME/oq-platform-ipt:$HOME/oq-platform-building-class
}

function exec_test() {
    export GEM_OPT_PACKAGES="$(python -c 'from openquakeplatform.settings import STANDALONE_APPS ; print(",".join(x for x in STANDALONE_APPS))')"

    if [ "$DEVEL_DATA" ]; then
        export GEM_PLA_ADMIN_ID=1
        export OQ_TEST="y"
    else
        export GEM_PLA_ADMIN_ID=1000
    fi    
    export DISPLAY=:1
    python -m openquake.moon.nose_runner --failurecatcher dev -s -v --with-xunit --xunit-file=xunit-platform-dev.xml $GIT_REPO/openquakeplatform/test # || true
}

function exec_set_map_thumbs() {
    export DISPLAY=:1
    python -m openquake.moon.nose_runner --failurecatcher dev -s -v --with-xunit --xunit-file=xunit-platform-dev.xml $GIT_REPO/openquakeplatform/set_thumb/mapthumbnail_test.py
}

function platform_install() {
    setup_postgres_once
    clone_platform
    oq_application
    install_geonode
    apply_data
    svir_world_data

    if [ "$NO_EXEC_TEST" != "notest" ] ; then
        initialize_test
        exec_set_map_thumbs
        exec_test
    fi    
}

platform_install
