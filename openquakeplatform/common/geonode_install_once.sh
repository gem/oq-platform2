#!/usr/bin/env bash

function setup_postgres_once() {                                                                                                                                 su - postgres <<EOF
createdb -E UTF8 -l en_US.UTF8 -T template0 geonode
createdb -E UTF8 -l en_US.UTF8 -T template0 geonode_data
psql -d geonode_data -c 'CREATE EXTENSION postgis'
EOF
su - postgres -c "psql" <<EOF
CREATE ROLE geonode WITH LOGIN PASSWORD '$psqlpass' SUPERUSER INHERIT;
EOF
}


function setup_django_once() {
    sed -i "s/THE_SECRET_KEY/$secretkey/g" /etc/geonode/local_settings.py
    sed -i "s/THE_DATABASE_PASSWORD/$psqlpass/g" /etc/geonode/local_settings.py
}

function one_time_setup() {                                                                                                                                          psqlpass=$(randpass 8 0)

    secretkey=$(randpass 18 0)

    setup_postgres_once
    setup_django_once
    # setup_apache_once # apache setup needs the every_time django setup since
    # it uses that to get the sitedir location
}

