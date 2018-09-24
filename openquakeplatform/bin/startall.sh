#!/bin/bash
source setall.sh
# export PYTHONPATH=$HOME/oq-platform2:$HOME/oq-platform-taxtweb:$HOME/oq-platform-ipt:$HOME/oq-platform-building-class
# disabled becaouse we want to insert 'nested_inlines' app before .admin
# export DJANGO_SETTINGS_MODULE='openquakeplatform.settings'
# export LOCKDOWN_GEONODE='True'
cd ~/geonode
paver -f $HOME/oq-platform2/pavement.py start -b 0.0.0.0:8000
sudo supervisorctl start openquake-webui

