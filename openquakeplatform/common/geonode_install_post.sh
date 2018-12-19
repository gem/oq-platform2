#!/bin/bash

# Location of the expanded GeoNode tarball
INSTALL_DIR=./package
# Location of the target filesystem, it may be blank
# or something like $(CURDIR)/debian/geonode/
TARGET_ROOT=''
# Tomcat webapps directory
TOMCAT_WEBAPPS=$TARGET_ROOT/var/lib/tomcat7/webapps
# Geoserver data dir, it will survive removals and upgrades
GEOSERVER_DATA_DIR=$TARGET_ROOT/var/lib/geoserver/geonode-data
# Place where GeoNode media is going to be served
GEONODE_WWW=$TARGET_ROOT/var/www/geonode
# Apache sites directory
APACHE_SITES=$TARGET_ROOT/etc/apache2/sites-available
# Place where the GeoNode virtualenv would be installed
GEONODE_LIB=$TARGET_ROOT/var/lib/geonode
# Path to preferred location of binaries (might be /usr/sbin for CentOS)
GEONODE_BIN=$TARGET_ROOT/usr/sbin/
# Path to place miscelaneous patches and scripts used during the install
GEONODE_SHARE=$TARGET_ROOT/usr/share/geonode
# Path to GeoNode configuration and customization
GEONODE_ETC=$TARGET_ROOT/etc/geonode
# Path to GeoNode logging folder
GEONODE_LOG=$TARGET_ROOT/var/log/geonode
# OS preferred way of starting or stopping services
# for example 'service httpd' or '/etc/init.d/apache2'
APACHE_SERVICE="invoke-rc.d apache2"
# sama sama
TOMCAT_SERVICE="invoke-rc.d tomcat7"

# For Ubuntu 16.04 (with PostGIS 2.2)
if [ -d "/usr/share/postgresql/9.5/contrib/postgis-2.2" ]
then
    POSTGIS_SQL_PATH=/usr/share/postgresql/9.5/contrib/postgis-2.2
    POSTGIS_SQL=postgis.sql
    GEOGRAPHY=1
else
    GEOGRAPHY=0
fi

function setup_postgres_every_time() {
    true # nothing to do. when we setup DB migrations they'll probably go here.
}


function setup_django_every_time() {
    # sudo pip install $GEONODE_SHARE/GeoNode-*.zip --no-dependencies --quiet

    sudo -H pip -v install /usr/share/geonode/GeoNode-*.zip --no-dependencies --quiet

    geonodedir=`python -c "import geonode;import os;print os.path.dirname(geonode.__file__)"`

    ln -sf $GEONODE_ETC/local_settings.py $geonodedir/local_settings.py
    # Set up logging symlink
    mkdir -p $GEONODE_LOG
    ln -sf /var/log/apache2/error.log $GEONODE_LOG/apache.log

    export DJANGO_SETTINGS_MODULE=geonode.settings

    django-admin migrate account --settings=geonode.settings
    geonode migrate --verbosity 0
    geonode loaddata $geonodedir/base/fixtures/initial_data.json
    geonode collectstatic --noinput --verbosity 0

    # Create an empty uploads dir
    mkdir -p $GEONODE_WWW/uploaded
    mkdir -p $GEONODE_WWW/uploaded/thumbs/
    # Apply the permissions to the newly created folders.
    chown www-data -R $GEONODE_WWW
    # Open up the permissions of the media folders so the python
    # processes like updatelayers and collectstatic can write here
    chmod 777 -R $GEONODE_WWW/uploaded
    chmod 777 -R $GEONODE_WWW/static
}

function setup_apache_every_time() {
    a2dissite 000-default

    #FIXME: This could be removed if setup_apache_every_time is called after setup_apache_once
    a2enmod proxy_http

    a2ensite geonode
    $APACHE_SERVICE restart
}


function postinstall() {
    setup_postgres_every_time
    setup_django_every_time
    setup_apache_every_time
    $TOMCAT_SERVICE restart
    $APACHE_SERVICE restart
}

