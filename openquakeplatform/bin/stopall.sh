#!/bin/bash
cd ~/geonode
sudo supervisorctl stop openquake-webui
paver stop

