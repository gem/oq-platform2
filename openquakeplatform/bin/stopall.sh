#!/bin/bash
cd ~/geonode
sudo supervisorctl stop openquake-webui
paver -f $HOME/oq-platform2/pavement.py stop

