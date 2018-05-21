#!/bin/bash
cd ~/geonode
sudo supervisorctl stop openquake-webui
paver -f /home/ubuntu/oq-platform2/pavement.py stop

