#!/bin/bash

set -x
set -e

sudo apt-get update
sudo apt install -y git python-virtualenv

# delete all folder used
sudo rm -rf env oq-platform2 geonode oq-platform-taxtweb oq-platform-building-class oq-platform-ipt

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

LXC_IP="$1"
GIT_BRANCH="$2"
GIT_GEO_REPO="2.6.x"
GEO_STABLE_HASH="aa5932d"
GIT_REPO="oq-platform2"

# clone oq-platform2
cd $HOME
git clone https://github.com/gem/oq-platform2.git
cd oq-platform2
git checkout deploy
pip install -e .

# clone ipt, taxtweb, building-classification-survey
cd $HOME
for repo in oq-platform-taxtweb oq-platform-ipt oq-platform-building-class; do
    # for repo in oq-platform-taxtweb; do
    if [ "$GIT_BRANCH" = "master" ]; then false ; else git clone -b "$GIT_BRANCH" https://github.com/gem/${repo}.git ; fi || git clone -b oq-platform2 https://github.com/gem/${repo}.git || git clone https://github.com/gem/${repo}.git
    cd ${repo}
    pip install -e .
done

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
# paver -f $HOME/$GIT_REPO/pavement.py oqsetup -l $LXC_IP -u localhost:8800 -s $HOME/geonode/data -dl geonode -dw 

# copy Geonode zip and oq_install script in package folder of Geonode
cd $HOME/geonode/package/
sudo cp -r $HOME/GeoNode-2.6.x.zip .
sudo cp $HOME/oq_install.sh . 

# install Geonode
cd ..
sudo ./package/oq_install.sh -s pre ~/oq-platform2/openquakeplatform/common/geonode_install_pre.sh
sudo ./package/oq_install.sh -s once ~/oq-platform2/openquakeplatform/common/geonode_install_once.sh

# enable wsgi apache
sudo apt-get install libapache2-mod-wsgi
sudo a2enmod wsgi
sudo invoke-rc.d apache2 restart

# sudo mv /etc/geonode/local_settings.py /etc/geonode/geonode_local_settings.py
# sudo cp  $HOME/oq-platform2/local_settings.py /etc/geonode/

sudo ./package/oq_install.sh -s post ~/oq-platform2/openquakeplatform/common/geonode_install_post.sh
sudo ./package/oq_install.sh -s setup_geoserver ~/oq-platform2/openquakeplatform/common/geonode_install_pre.sh
# sudo ./package/install.sh -s setup_apache_once ~/oq-platform2/openquakeplatform/common/geonode_install_setup_apache_once.sh

sudo sed -i '1 s@^@WSGIPythonHome /home/ubuntu/env\n@g' /etc/apache2/sites-enabled/geonode.conf
sudo invoke-rc.d apache2 restart
