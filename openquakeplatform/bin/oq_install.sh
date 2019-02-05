#!/usr/bin/env bash 
# GeoNode installer script
#
# using getopts
#

if [ $GEM_SET_DEBUG ]; then
    set -x
fi
# set -e

if [ "$1" = "-d" ]; then
    OQ_DEVEL_DATA=y
    shift
fi

source ~/env/bin/activate

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

function setup_directories() {
    mkdir -p $GEOSERVER_DATA_DIR
    mkdir -p $GEONODE_WWW/static
    mkdir -p $GEONODE_WWW/uploaded
    mkdir -p $GEONODE_WWW/wsgi
    mkdir -p $APACHE_SITES
    mkdir -p $GEONODE_BIN
    mkdir -p $GEONODE_ETC
    mkdir -p $GEONODE_ETC/media
    mkdir -p $GEONODE_ETC/templates
    mkdir -p $GEONODE_SHARE
}

function reorganize_configuration() {
    cp -rp $INSTALL_DIR/support/geonode.apache $APACHE_SITES/geonode.conf
    cp -rp $INSTALL_DIR/support/geonode.wsgi $GEONODE_WWW/wsgi/
    cp -rp $INSTALL_DIR/support/geonode.robots $GEONODE_WWW/robots.txt
    cp -rp $INSTALL_DIR/support/geonode.binary $GEONODE_BIN/geonode
    cp -rp $INSTALL_DIR/GeoNode*.zip $GEONODE_SHARE
    cp -rp $INSTALL_DIR/support/geonode.updateip $GEONODE_BIN/geonode-updateip
    cp -rp $INSTALL_DIR/support/geonode.admin $GEONODE_SHARE/admin.json
    cp -rp $INSTALL_DIR/support/geonode.local_settings $GEONODE_ETC/local_settings.py

    chmod +x $GEONODE_BIN/geonode
    chmod +x $GEONODE_BIN/geonode-updateip
}

function preinstall() {
    setup_directories
    reorganize_configuration
    echo "Fine preinstall"
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
    source ~/env/bin/activate
    
    pip -v install /usr/share/geonode/GeoNode-*.zip --no-dependencies --quiet
    geonodedir=`python -c "import geonode;import os;print os.path.dirname(geonode.__file__)"`

    ln -sf /etc/geonode/local_settings.py $HOME/env/lib/python2.7/site-packages/geonode/local_settings.py
    ln -sf /usr/lib/python2.7/dist-packages/osgeo $HOME/env/lib/python2.7/site-packages

    # Set up logging symlink
    mkdir -p $GEONODE_LOG
    ln -sf /var/log/apache2/error.log $GEONODE_LOG/apache.log

    export DJANGO_SETTINGS_MODULE=geonode.settings

    django-admin migrate account --settings=geonode.settings
    # geonode runserver &
    geonode migrate --verbosity 0
    geonode loaddata $geonodedir/base/fixtures/initial_data.json
    geonode collectstatic --noinput --verbosity 0

    if [ "$ OQ_DEVEL_DATA" = "y" ]; then
        geonode createsuperuser
    fi

    # Create an empty uploads dir
    mkdir -p $GEONODE_WWW/uploaded
    # mkdir -p $GEONODE_WWW/uploaded/thumbs/
    ln -sf $HOME/env/lib/python2.7/site-packages/geonode/uploaded/thumbs $GEONODE_WWW/uploaded
    mkdir -p $HOME/env/local/lib/python2.7/site-packages/geonode/uploaded
    mkdir -p $HOME/env/local/lib/python2.7/site-packages/geonode/uploaded/layers
    mkdir -p $HOME/env/local/lib/python2.7/site-packages/geonode/uploaded/documents

    # Apply the permissions to the newly created folders.
    sudo chown www-data -R $GEONODE_WWW

    # Open up the permissions of the media folders so the python
    # processes like updatelayers and collectstatic can write here
    chmod 775 -R $GEONODE_WWW/uploaded
    chmod 775 -R $GEONODE_WWW/static
    chmod 775 -R $HOME/env/local/lib/python2.7/site-packages/geonode/uploaded/
    chmod 775 -R $HOME/env/local/lib/python2.7/site-packages/geonode/uploaded/layers
    chmod 775 -R $HOME/env/local/lib/python2.7/site-packages/geonode/uploaded/documents
    chmod 775 -R $HOME/env/local/lib/python2.7/site-packages/geonode/static_root

    # for install geonode
    sudo rm -rf /var/www/geonode/static
    sudo ln -sf $HOME/env/lib/python2.7/site-packages/geonode/static_root/ /var/www/geonode/static

    # ipt folder
    sudo chmod 775 -R $GEONODE_WWW 
    cd $GEONODE_WWW
    mkdir data                  
    sudo chown -R www-data.www-data $GEONODE_WWW/data
}

function setup_apache_once() {
    chown www-data -R $GEONODE_WWW
    a2enmod proxy_http

    sed -i '1d' $APACHE_SITES/geonode.conf
    sed -i "1i WSGIDaemonProcess geonode user=www-data threads=15 processes=2" $APACHE_SITES/geonode.conf
    sudo sed -i '1 s@^@WSGIPythonHome /home/openquake/env\n@g' $APACHE_SITES/geonode.conf

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
    # wget http://ftp.openquake.org/oq-platform2/data-2.9.x-oauth2.zip
    mv geoserver-2.9.x-oauth2.war geoserver.war
    mv geoserver.war $TOMCAT_WEBAPPS

    ## Symbolic link to solve spatialite warning of Geoserver
    # sudo ln -sf /usr/lib/x86_64-linux-gnu/libproj.so.9 /usr/lib/x86_64-linux-gnu/libproj.so.0

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

if [ $# -eq 1 ]
then
    printf "Sourcing %s as the configuration file\n" $1
    source $1
else
    printf "Usage: %s: [-s value] configfile\n" $(basename $0) >&2
        exit 2
fi

if [ "$stepflag" ]                                                              
then
printf "\tStep: '$stepval specified\n"
else
    stepval="all"
    echo "heh"
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
        printf "\tValid values for step parameter are: 'pre', 'post','all'\n"
        printf "\tDefault value for step is 'all'\n"
        ;;
esac                                     
