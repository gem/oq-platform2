#!/bin/bash

set -x
set -e

sudo apt-get update
sudo apt install -y git python-virtualenv

sudo rm -rf env oq-platform2 geonode
# sudo rm -rf env geonode

# Create and source virtual env
virtualenv env
source $HOME/env/bin/activate

sudo apt install -y python-dev libpq-dev libgdal-dev openjdk-8-jdk-headless 
pip install numpy
sudo apt install -y apache2
python -m pip install "django<2"
pip install scipy

LXC_IP="$1"
GIT_GEO_REPO="2.6.x"
GEO_STABLE_HASH="aa5932d"
GIT_REPO="oq-platform2"

usage() {
    local com="$1" ret="$2"
    # echo "${com} <--help|-p> <--hostname|-H> hostname [<--db_name|-d> db_name] [<--db_user|-u> db_user] [<--webuiurl|-w> <addr>] [<--oq_engserv_key|-k> <key>] [<--oq_bing_key|-B> <bing-key>]"
    echo "${com} <--lxc_ip| add ip>"
    exit $ret
}


# clone oq-platform2
cd $HOME
git clone https://github.com/gem/oq-platform2.git
cd oq-platform2
git checkout deploy

# clone geonode
cd $HOME
git clone --depth=1 -b "$GIT_GEO_REPO" https://github.com/GeoNode/geonode.git
cd $HOME/geonode
git checkout "$GEO_STABLE_HASH"
pip install -r requirements.txt
pip install -r $HOME/$GIT_REPO/gem_geonode_requirements.txt

pip install -e .

sudo apt install -y python-gdal gdal-bin


# Create local_settings with pavement from repo
paver -f $HOME/$GIT_REPO/pavement.py oqsetup -l $LXC_IP -u localhost:8800 -s $HOME/geonode/data

cd $HOME/geonode/package/
sudo cp -r $HOME/GeoNode-2.6.x.zip .
sudo cp $HOME/oq_install.sh . 

cd ..
sudo ./package/oq_install.sh -s pre ~/oq-platform2/openquakeplatform/common/geonode_install_pre.sh
sudo ./package/oq_install.sh -s once ~/oq-platform2/openquakeplatform/common/geonode_install_once.sh

# enable wsgi apache
sudo apt-get install libapache2-mod-wsgi
sudo a2enmod wsgi
sudo invoke-rc.d apache2 restart

# sudo mv /etc/geonode/local_settings.py /etc/geonode/geonode_local_settings.py
# sudo rm /usr/local/lib/python2.7/dist-packages/geonode/local_settings.py
# sudo cp  $HOME/oq-platform2/local_settings.py /etc/geonode/
# sudo ln -sf /etc/geonode/local_settings.py /usr/local/lib/python2.7/dist-packages/geonode/local_settings.py

sudo ./package/oq_install.sh -s setup ~/oq-platform2/openquakeplatform/common/geonode_install_pre.sh
sudo ./package/oq_install.sh -s post ~/oq-platform2/openquakeplatform/common/geonode_install_post.sh
# sudo ./package/install.sh -s setup_apache_once ~/oq-platform2/openquakeplatform/common/geonode_install_setup_apache_once.sh


# ln -sf /usr/lib/python2.7/dist-packages/osgeo env/lib/python2.7/site-packages/osgeo

sudo sed -i '1 s@^@WSGIPythonHome /home/ubuntu/env\n@g' /etc/apache2/sites-enabled/geonode.conf
sudo invoke-rc.d apache2 restart
