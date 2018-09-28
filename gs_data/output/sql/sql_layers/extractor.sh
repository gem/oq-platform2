#!/bin/bash
IFS='
'
for lay in $(cat in/layers_list.txt); do
    sudo -u postgres psql -d geonode_dev -c '\copy '$lay' FROM 'out/$lay''
done
