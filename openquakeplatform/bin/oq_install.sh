#!/usr/bin/env bash 
# GeoNode installer script
#
# using getopts
#

if [ $GEM_SET_DEBUG ]; then
     set -x
fi
set -e

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

while getopts 's:' OPTION
do
    case $OPTION in
    s)
        stepflag=1
        stepval="$OPTARG"
        ;;
    ?)
        printf "Usage: %s: [-s value] configfile\n" $(basename $0) >&2
        exit 2
        ;;
    esac
done
shift $(($OPTIND - 1))

function unsudo () {
    local normal_user cmd="$1"

    normal_user="$(logname)"
    sudo su - -c "$cmd" $normal_user
}

function setup_directories() {
    mkdir -p $GEOSERVER_DATA_DIR
    mkdir -p $GEONODE_WWW/static
    mkdir -p $GEONODE_WWW/wsgi
    mkdir -p $APACHE_SITES
    mkdir -p $GEONODE_BIN
    mkdir -p $GEONODE_ETC
    mkdir -p $GEONODE_ETC/media
    mkdir -p $GEONODE_ETC/templates
    mkdir -p $GEONODE_SHARE

    # Create an empty uploads dir
    mkdir -p $GEONODE_WWW/uploaded/{thumbs,layers,documents}

    # Open up the permissions of the media folders so the python
    # processes like updatelayers and collectstatic can write here
    chmod 775 -R $GEONODE_WWW/uploaded
    chmod g+s -R $GEONODE_WWW/uploaded

    # Apply the permissions to the newly created folders.
    chgrp www-data -R $GEONODE_WWW/uploaded
}

function reorganize_configuration() {
    cp $INSTALL_DIR/support/geonode.apache $APACHE_SITES/geonode.conf
    cp $INSTALL_DIR/support/geonode.wsgi $GEONODE_WWW/wsgi/
    if [ "$DEVEL_DATA" -o "$DATA_PROD" ]; then
        sed -i 's/import os/import os\nos.umask(002)/g' $GEONODE_WWW/wsgi/geonode.wsgi
    fi
    cp $INSTALL_DIR/support/geonode.robots $GEONODE_WWW/robots.txt
    cp $INSTALL_DIR/support/geonode.binary $GEONODE_BIN/geonode
    cp $INSTALL_DIR/GeoNode*.zip $GEONODE_SHARE
    cp $INSTALL_DIR/support/geonode.updateip $GEONODE_BIN/geonode-updateip
    cp $INSTALL_DIR/support/geonode.admin $GEONODE_SHARE/admin.json
    cp $INSTALL_DIR/support/geonode.local_settings $GEONODE_ETC/local_settings.py

    chmod +x $GEONODE_BIN/geonode
    chmod +x $GEONODE_BIN/geonode-updateip
}

function preinstall() {
    setup_directories
    reorganize_configuration
    echo "End preinstall"
}

function randpass() {
    [ "$2" == "0" ] && CHAR="[:alnum:]" || CHAR="[:graph:]"
    cat /dev/urandom | tr -cd "$CHAR" | head -c ${1:-32}
    echo
}

function setup_postgres_every_time() {
    true # nothing to do. when we setup DB migrations they'll probably go here.
}

function setup_django_every_time() {
    echo "setup_django_every_time:"
    source  /var/lib/geonode/env/bin/activate
    
    pip -v install /usr/share/geonode/GeoNode-*.zip --no-dependencies --quiet
    geonodedir=`python -c "import geonode;import os;print os.path.dirname(geonode.__file__)"`

    ln -sf /etc/geonode/local_settings.py /var/lib/geonode/env/lib/python2.7/site-packages/geonode/local_settings.py
    ln -sf /usr/lib/python2.7/dist-packages/osgeo  /var/lib/geonode/env/lib/python2.7/site-packages

    # Set up logging symlink
    mkdir -p $GEONODE_LOG
    ln -sf /var/log/apache2/error.log $GEONODE_LOG/apache.log

    export DJANGO_SETTINGS_MODULE=geonode.settings

    unsudo 'source /var/lib/geonode/env/bin/activate ; django-admin migrate account --settings=geonode.settings'
    unsudo 'source /var/lib/geonode/env/bin/activate ; geonode migrate --verbosity 0'
    unsudo 'source /var/lib/geonode/env/bin/activate ; geonode loaddata $geonodedir/base/fixtures/initial_data.json'
    geonode collectstatic --noinput --verbosity 0

    if [ -z "$DEVEL_DATA" ]; then
        unsudo 'source /var/lib/geonode/env/bin/activate ; geonode createsuperuser'
    fi

    # ipt folder
    mkdir $GEONODE_WWW/data
    chgrp www-data -R $GEONODE_WWW/data
    chmod 775 $GEONODE_WWW/data
    if [ "$DEVEL_DATA" -o "$DATA_PROD" ]; then
        chmod g+s $GEONODE_WWW/data
    fi
}

function setup_apache_once() {
    chown www-data -R $GEONODE_WWW
    a2enmod proxy_http

    sed -i '1d' $APACHE_SITES/geonode.conf
    sed -i "1i WSGIDaemonProcess geonode user=www-data threads=15 processes=2" $APACHE_SITES/geonode.conf
    sed -i '1 s@^@WSGIPythonHome /var/lib/geonode/env\n@g' $APACHE_SITES/geonode.conf

    #FIXME: This could be removed if setup_apache_every_time is called after setup_apache_once
    $APACHE_SERVICE restart
}

function setup_apache_every_time() {
    a2dissite 000-default

    #FIXME: This could be removed if setup_apache_every_time is called after setup_apache_once
    a2enmod proxy_http

    a2ensite geonode
    $APACHE_SERVICE restart
}

function setup_geoserver() {
    cd $HOME/geonode
    wget http://ftp.openquake.org/oq-platform2/geoserver-2.9.x-oauth2.war
    mv geoserver-2.9.x-oauth2.war geoserver.war
    mv geoserver.war $TOMCAT_WEBAPPS

    $TOMCAT_SERVICE restart

    ## Symbolic link to solve spatialite warning of Geoserver
    sudo ln -sf /usr/lib/x86_64-linux-gnu/libproj.so.9 /usr/lib/x86_64-linux-gnu/libproj.so.0
}

function postinstall() {
    setup_postgres_every_time
    setup_django_every_time
    setup_apache_every_time
    $TOMCAT_SERVICE restart
    $APACHE_SERVICE restart
}

function once() {
    echo "Still need to implement the onetime setup."
    exit 1
}

if [ $# -eq 1 ]; then
    printf "Sourcing %s as the configuration file\n" $1
    source $1
else
    printf "Usage: %s: [-s value] configfile\n" $(basename $0) >&2
        exit 2
fi

if [ "$stepflag" ]; then
    printf "\tStep: '$stepval specified\n"
else
    stepval="all"
fi

case $stepval in
    pre)
        echo "Running GeoNode preinstall ..."
        preinstall
        ;;
    post)
        echo "Running GeoNode postinstall ..."
        postinstall
        ;;
    setup_apache_once)
        echo "Configuring Apache ..."
        setup_apache_once
        ;;
    setup_geoserver)
        echo "Setup Geoserver ..."
        setup_geoserver
        ;;
    all)
        echo "Running GeoNode installation ..."
        preinstall
        setup_geoserver
        postinstall
        setup_apache_once
        ;;
    *)
        printf "\tValid values for step parameter are: 'pre', 'post','setup_apache_once','setup_geoserver'\n"
        printf "\tDefault value for step is 'all'\n"
        ;;
esac                                     
