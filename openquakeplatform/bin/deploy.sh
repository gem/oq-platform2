#!/bin/bash
# Copyright (c) 2013-2018, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake.  If not, see <http://www.gnu.org/licenses/>.

if [ $GEM_SET_DEBUG ]; then
    set -x
fi
set -e
# export PS4='+${BASH_SOURCE}:${LINENO}:${FUNCNAME[0]}: '

#
# Guidelines
#
#    Configuration file manglings are done only if they not appear already made.
#

# TIPS
#    to remove all:
#
# PUBLIC GLOBAL VARS
# version managements - use "master" or tagname to move to other versions

export GEM_OQ_PLATF_GIT_REPO=git://github.com/gem/oq-platform2.git

# export GEM_OQ_PLATF_SUBMODS="openquakeplatform/openquakeplatform/static/Leaflet
# openquakeplatform/openquakeplatform/static/Leaflet.draw
# openquakeplatform/openquakeplatform/static/wax"

# export MIGRATIONS_HISTORY="/var/lib/openquake/platform/migrations/history"

if [ -f /etc/openquake/platform2/local_settings.py ]; then
    GEM_IS_INSTALL=n
else
    GEM_IS_INSTALL=y
fi

GEM_DB_NAME='oqplatform'
GEM_DB_USER='oqplatform'
GEM_DB_PASS='the-password'
GEM_WEBUIURL='localhost.localdomain:8800'
GEM_OQ_ENGSERV_KEY='oq-platform2'
GEM_OQ_BING_KEY=''

GEM_APP_LIST=('world' 'isc_viewer' 'ghec_viewer' 'exposure' 'vulnerability' 'svir' 'hazus' 'irv' 'ipt')

GEM_WEBDIR=/var/www/openquake/platform

GEM_LOCAL_SETTINGS_TMPL="local_settings.py.tmpl"
GEM_LOCAL_SETTINGS="/etc/openquake/platform/local_settings.py"

#
#   geoserver related vars
#
# base data dir in ubuntu production environment
GEM_GS_DATADIR="/usr/share/geoserver/data"
# geoserver default workspace
GEM_GS_WS_NAME="oqplatform"
# geoserver default datastore
GEM_GS_DS_NAME="oqplatform"

# stable hash repo geonode
GIT_GEO_REPO="2.6.x"
GEO_STABLE_HASH="aa5932d"

#
#   postgis related vars
#
# POSTGIS_DIR=/usr/share/postgresql/9.1/contrib/
# POSTGIS_FILES=( ${POSTGIS_DIR}{postgis-1.5/postgis,postgis-1.5/spatial_ref_sys,postgis_comments}.sql )
# export NL='
# '
# export TB='	'

#
#  functions

#
#  <name_long>|<opt>[:],[...]
#
declare -A globargs

parsargs () {
    local frmt="$1"
    local st=0 skip=0
    local i e
    shift
    declare -a args=("$@")
    for i in $(seq 0 $(( ${#args[*]} - 1 )) ); do
        arg="${args[$i]}"
        if [ $skip -gt 0 ]; then
            skip=$((skip - 1))
            continue
        fi
        # echo "ARG: [${args[$i]}]"
        if [ $st -eq 0 ]; then
            if [ "${arg:0:2}" = "--" ]; then
                if [ "${arg:2:1}" = "" ]; then
                    return
                fi
                # long name case
                name="$(echo "${arg:2}" | cut -d '=' -f 1)"
                if ! echo "$frmt" | tr ',' '\n' | grep -q "$name|[a-zA-Z:]\+" ; then
                    echo "argument --$name not found"
                    exit 1
                fi

                if echo "$frmt" | tr ',' '\n' | grep -q "\b$name|[a-zA-Z]\+:" ; then
                    # echo "WITH PARAMETER"
                    if echo "$arg" | grep "^--${name}=" ; then
                        # with equal case
                        value="$(echo "${arg:2}" | cut -d '=' -f 2-)"
                    else
                        value=${args[$(( i + 1 ))]}
                        skip=1
                    fi
                else
                    value="true"
                fi
                # echo "LONG NAME: [$name] VAL: [$value]"
                globargs[$name]="$value"
            elif [ "${arg:0:1}" = "-" -a "${arg:1:1}" != "-" ]; then
                args_short="${arg:1}"
                for e in $(seq 0 $(( ${#args_short} - 1 )) ); do
                    arg_short="${args_short:$e:1}"
                    if ! echo "$frmt" | tr ',' '\n' | grep -q "|$arg_short:\?$"; then
                        echo "argument -$arg_short not found"
                        exit 1
                    fi
                    name="$(echo "$frmt" | tr ',' '\n' | grep "|$arg_short:\?$" | cut -d '|' -f 1)"
                    # echo "LETTER[$e]: $arg_short  NAME [$name]"
                    if echo "$frmt" | tr ',' '\n' | grep -q "\b$name|[a-zA-Z]\+:" ; then
                        # echo "WITH PARAMETER"
                        if [ "${args_short:$((e + 1)):1}" != "" ]; then
                            echo "argument -$arg_short require argument"
                            exit 1
                        fi
                        value=${args[$(( i + 1 ))]}
                        skip=1
                        # echo "SHORT NAME: [$name] VAL: [$value]"
                        globargs[$name]="$value"
                        break
                    else
                        value="true"
                        # echo "SHORT NAME: [$name] VAL: [$value]"
                        globargs[$name]="$value"
                    fi
                done
            fi
        fi
    done
}

#
#
world_dataloader () {
    local oqpdir="$1" db_name="$2" bdir

    if [ -f "private_data/world.json.bz2" ]; then
        bdir="private_data"
    else
        bdir="${oqpdir}/world/dev_data"
    fi
    openquakeplatform loaddata "${bdir}/world.json.bz2"
}

#
#
svir_dataloader () {
    local oqpdir="$1" db_name="$2" bdir

    if [ -f "private_data/svir.json.bz2" ]; then
        bdir="private_data"
    else
        bdir="${oqpdir}/svir/dev_data"
    fi
    openquakeplatform loaddata "${bdir}/svir.json.bz2"
}

#
#
vulnerability_dataloader () {
    local oqpdir="$1" db_name="$2" bdir

    openquakeplatform loaddata ${oqpdir}/vulnerability/post_fixtures/initial_data.json
    if [ "$GEM_IS_INSTALL" == "y" ]; then
        # if it is an update we assume an already populated set of curves.
        # Changing the country table produce with high probability a corruption of the db.
        if [ -f "private_data/vuln_geo_applicability_data.csv" ]; then
            bdir="private_data"
        else
            bdir="${oqpdir}/vulnerability/dev_data"
        fi
        openquakeplatform import_vuln_geo_applicability_csv "${bdir}/vuln_geo_applicability_data.csv"
    fi
    openquakeplatform vuln_groups_create
}

#
#
passwd_create () {
    python -c "import string ; import random
def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))
print id_generator()"
}

#
#
function_exists () {
    local fname="$1"
    set | grep -q "^$fname "
}

#
#
locset_create () {
    local oqpdir gem_hostname gem_secr_key gem_db_name gem_db_user gem_db_pass
    local gem_webuiurl gem_oq_engserv_key gem_oq_bing_key
    oqpdir="$1" ; shift
    gem_hostname="$1" ; shift
    gem_secr_key="$1" ; shift
    gem_db_name="$1" ; shift
    gem_db_user="$1" ; shift
    gem_db_pass="$1" ; shift
    gem_webuiurl="$1" ; shift
    gem_oq_engserv_key="$1"; shift
    gem_oq_bing_key="$1"

    if [ -f "$GEM_LOCAL_SETTINGS" ]; then
        return 1
    fi
    python -c "
import string, random
local_settings = open('${oqpdir}/$GEM_LOCAL_SETTINGS_TMPL', 'r').read()
with open('$GEM_LOCAL_SETTINGS', 'w') as fh:
    fh.write(local_settings % dict(hostname='${gem_hostname}',
                                   siteurl='${gem_hostname}',
                                   db_name='${gem_db_name}',
                                   db_user='${gem_db_user}',
                                   db_pass='${gem_db_pass}',
                                   geonode_port=80,
                                   geoserver_port=8080,
                                   webuiurl='${gem_webuiurl}',
                                   oq_engserv_key='${gem_oq_engserv_key}',
                                   oq_bing_key='${gem_oq_bing_key}',
                                   oq_secret_key='${gem_secr_key}',
                                   mediaroot='/var/www/openquake/platform/uploaded',
                                   staticroot='/var/www/openquake/platform/static/',
                                   is_gem_experimental=False,
                                   datadir='/var/www/openquake/platform/data/',
                                   ))"
}

#
#
# db_user_exists () {
#     local db_user="$1"
# 
#     su - -c "echo \"SELECT rolname FROM pg_roles WHERE rolname = '${db_user}';\" \
#              | psql -A -t | wc -l" postgres
# }
# 
# #
# #
# db_base_exists () {
#     local db_name="$1"
# 
#     su - -c "echo \"SELECT datname FROM pg_database WHERE datname = '$db_name';\" | psql -A -t | wc -l" postgres
# }
# 
# #
# #
# db_gis_exists () {
#     local db_name="$1"
# 
#     su - -c "echo \"SELECT proname FROM pg_proc WHERE proname = 'postgis_full_version';\" | psql -A -t \"$db_name\" | wc -l" postgres
# }
# 
# #
# #
# db_user_create () {
#     local db_user="$1" db_pass="$2" aex
# 
#     aex="$(db_user_exists "$db_user")"
#     if [ $aex -gt 0 ]; then
#         echo "WARNING: database user [$db_user] already exists!" >&2
#         return 1
#     fi
# 
#     su - -c "echo \"CREATE ROLE ${db_user} ENCRYPTED PASSWORD '${db_pass}' SUPERUSER CREATEDB NOCREATEROLE INHERIT LOGIN;\" | psql" postgres
# }

#
#
# db_base_create () {
#     local db_name="$1" owner="$2" aex
# 
#     aex="$(db_base_exists "$db_name")"
#     if [ $aex -gt 0 ]; then
#         echo "WARNING: database [$db_name] already exists!" >&2
#         return 1
#     fi
# 
#     su - -c "echo \"CREATE DATABASE ${db_name} OWNER ${owner};\" | psql" postgres
# }
# 
# #
# #
# db_gis_create () {
#     local db_name="$1" aex
# 
#     aex="$(db_gis_exists "$db_name")"
#     if [ $aex -gt 0 ]; then
#         echo "WARNING: database [$db_name] has already GIS extensions!" >&2
#         return 1
#     fi
# 
#     for i in "${POSTGIS_FILES[@]}"; do
#         su - -c "cat "$i" | psql ${db_name}" postgres
#     done
# }

# deps_info () {
#         cat <<EOF
#     sudo apt-get install imagemagick xmlstarlet python-scipy
#     sudo pip install Pillow==2.3.1 --no-deps
#     sudo pip install South==0.8.4 --no-deps
#     sudo pip install django-photologue==2.6.1 --no-deps
# EOF
# }

#
oq_platform_install () {
    local norm_user norm_dir gem_hostname norm_home ret a distdesc rv
    local cur_step

    if [ "${globargs['norm_user']}" == "" -o "${globargs['norm_dir']}" == ""  -o "${globargs['hostname']}" == "" ]; then
        usage "$0" 1
    fi
    norm_user="${globargs['norm_user']}"
    norm_dir="${globargs['norm_dir']}"
    gem_hostname="${globargs['hostname']}"

    gem_db_name="${globargs['db_name']:-$GEM_DB_NAME}"
    gem_db_user="${globargs['db_user']:-$GEM_DB_USER}"
    gem_db_pass="${globargs['db_pass']:-$GEM_DB_PASS}"

    gem_webuiurl="${globargs['webuiurl']:-$GEM_WEBUIURL}"
    gem_oq_engserv_key="${globargs['oq_engserv_key']:-$GEM_OQ_ENGSERV_KEY}"
    gem_oq_bing_key="${globargs['oq_bing_key']:-$GEM_OQ_BING_KEY}"

    cur_step=0

    norm_home="$(grep "$norm_user" /etc/passwd | cut -d ":" -f 6)"

    # switch to false to extract previous password value
    if [ "$GEM_IS_INSTALL" == "y" ]; then
        gem_db_pass="$(passwd_create)"
        gem_secr_key="$(python -c "import string, random ; print ''.join(random.choice(string.ascii_letters + string.digits + '%$&()=+-|#@?') for _ in range(50))")"

    else
        gem_db_pass="$(python -c "execfile('/etc/openquake/platform/local_settings.py',globals() ,locals() ); print DATABASES['default']['PASSWORD']" )" ;
        gem_secr_key="$(python -c "execfile('/etc/openquake/platform/local_settings.py',globals() ,locals() ); print SECRET_KEY" )" ;
        if [ -z "$gem_oq_bing_key" ]; then
            gem_oq_bing_key="$(python -c "execfile('/etc/openquake/platform/local_settings.py',globals() ,locals() ); print BING_KEY['bing_key']" )" ;
        fi
    fi

    # reset and install disabled
    if [ "$GEM_IS_INSTALL" == "y" ]; then
        service tomcat7 stop                       || true
        sleep 5                                    || true
        pip uninstall -y openquakeplatform         || true
        su - -c "dropdb ${gem_db_name}" postgres   || true
        su - -c "dropuser ${gem_db_user}" postgres || true
        rm -rf /etc/openquake/platform             || true
        a2dissite geonode                          || true
        a2dissite oqplatform                       || true
        service tomcat7 start                      || true
    fi

    apt-get update
    apt-get install -y python-software-properties
    # add-apt-repository -y "deb http://ftp.openquake.org/ubuntu precise main"
    # GeoNode
    add-apt-repository -y "ppa:openquake/ppa"
    # OQ Engine
    add-apt-repository -y "ppa:openquake/release-3.1"
    # add Ariel Nuñez key
    # apt-key adv --keyserver keyserver.ubuntu.com --recv-keys  925F51BF

    # add Matteo Nastasi key
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys  CF62A55B

    apt-get update
    apt-get install -y --force-yes python-oq-engine

    # clone geonode
    git clone --depth=1 -b "$GIT_GEO_REPO" https://github.com/GeoNode/geonode.git
    cd geonode
    git checkout "$GEO_STABLE_HASH"

    # Install geonode
    sudo ./package/install.sh -s pre ~/oq-platform2/openquakeplatform/common/geonode_install_pre.sh
    sudo ./package/install.sh -s pre ~/oq-platform2/openquakeplatform/common/geonode_install_post.sh

    #install dependencies vulnerability and ipt
    extra_deps_install() {
        python -m pip install "django<2"
        pip install django-nested-inline
        pip install django_extras
        pip install -e git+git://github.com/gem/django-chained-selectbox.git@pla26#egg=django-chained-selectbox-0.2.2
        pip install -e git+git://github.com/gem/django-nested-inlines.git@pla26#egg=django-nested-inlines-0.1.4
        pip install -e git+git://github.com/gem/django-chained-multi-checkboxes.git@pla26#egg=django-chained-multi-checkboxes-0.4.1
        pip install -e git+git://github.com/gem/wadofstuff-django-serializers.git@pla26#egg=wadofstuff-django-serializers-1.1.2
    }

    cd oq-platform2/openquakeplatform

    # install extra deps and create venv
    if [ -d ~/env ]; then
        rm -rf ~/env
    fi
    virtualenv ~/env

    source ~/env/bin/activate

    extra_deps_install

    pip install scipy

    # deps_install
    pip install . -U --no-deps
    cd -
    oqpdir="$(python -c "import openquakeplatform;import os;print os.path.dirname(openquakeplatform.__file__)")"

    if [ "$GEM_IS_INSTALL" != "y" ]; then
        rm -rf output.bak
        rm -rf geoserver.dump.bak
        if [ -e output ]; then
            mv output output.bak
        fi
        if [ -e geoserver.dump ]; then
            mv geoserver.dump geoserver.dump.bak
        fi
        ${oqpdir}/bin/oq-gs-builder.sh dump
        mv output geoserver.dump
    fi
    mkdir -p /etc/openquake/platform
    if [ "$GEM_IS_INSTALL" != "y" ]; then
        mv /etc/openquake/platform/local_settings.py /etc/openquake/platform/local_settings.py.orig
    fi

    locset_create "$oqpdir" "$gem_hostname" "$gem_secr_key" "$gem_db_name" "$gem_db_user" "$gem_db_pass" "${gem_webuiurl}" "${gem_oq_engserv_key}" "${gem_oq_bing_key}"

    if [ "$GEM_IS_INSTALL" != "y" ]; then
	mv /etc/openquake/platform/local_settings.py /etc/openquake/platform/local_settings.py.new
	mv /etc/openquake/platform/local_settings.py.orig /etc/openquake/platform/local_settings.py

        while [ true ]; do
            diff -u /etc/openquake/platform/local_settings.py /etc/openquake/platform/local_settings.py.new || true
            read -p "Ctrl+C to interrupt or open a new terminal and edit /etc/openquake/platform/local_settings.py.new, then type 'y' to continue or press <enter> to update the diff output: " qvest
            qvest="$(echo "$qvest" | tr 'A-Z' 'a-z')"
            if [ "$qvest" == "y" ]; then
                break
            fi
        done

        mv /etc/openquake/platform/local_settings.py.new /etc/openquake/platform/local_settings.py
    fi

    cp "${oqpdir}/apache2/oqplatform" /etc/apache2/sites-available/
    ln -sf /etc/openquake/platform/local_settings.py "${oqpdir}"
    a2dissite geonode
    a2ensite oqplatform
    mkdir -p "$GEM_WEBDIR"
    cp "${oqpdir}/wsgi.py"* "$GEM_WEBDIR"
    cp "${oqpdir}/bin/openquakeplatform" "/usr/sbin/"
    chmod a+x "/usr/sbin/openquakeplatform"
    mkdir -p /etc/openquake/platform/media

    if (kill -0 $(cat /var/run/apache2.pid)) >/dev/null 2>&1; then
        service apache2 restart
    elif (kill -0 $(cat /var/run/gunicorn/platform-prod.pid)) >/dev/null 2>&1; then
        service gunicorn restart
    fi

    if [ "$GEM_IS_INSTALL" == "y" ]; then
        db_user_create "$gem_db_user" "$gem_db_pass"
        db_base_create "$gem_db_name" "$gem_db_user"
        db_gis_create  "$gem_db_name"

        #
        #  database population (fixtures)
        #  FIXME this must be run also on NEW applications (if any exists) during upgrades;
        #        OLD applications that changed should use migrations and must be skipped here
        for app in "${GEM_APP_LIST[@]}"; do
            if function_exists "${app}_fixtureupdate"; then
                "${app}_fixtureupdate" "$oqpdir"
            fi
        done
        openquakeplatform syncdb --all --noinput
    else
        echo "WARNING: this operation could be destructive for the current version of oqplatform database schema, do proper backup before proceeding."
        read -p "Open a new terminal, migrate the application database schema manually and then press <enter> to continue: " qvest
        openquakeplatform syncdb --noinput
    fi

    openquakeplatform collectstatic --noinput

    #
    # Update Django 'sites' with real hostname
    openquakeplatform fixsitename

    if [ "$GEM_IS_INSTALL" == "y" ]; then
        # Load our users. Default password must be changed
        openquakeplatform loaddata ${oqpdir}/common/fixtures/*.json

        #
        #  database population (external datasets)
        #  FIXME this must be run also on NEW applications (if any exists) during upgrades;
        #        OLD applications that changed should use migrations and must be skipped here
        for app in "${GEM_APP_LIST[@]}"; do
            if function_exists "${app}_dataloader"; then
                "${app}_dataloader" "$oqpdir" "$gem_db_name"
            fi
        done
    fi

    #
    #  geoserver structure population
    rm -rf "${oqpdir}/build-gs-tree"
    if [ "$GEM_IS_INSTALL" != "y" ]; then
        cp -r geoserver.dump "${oqpdir}/build-gs-tree"
    fi
    # ${oqpdir}/bin/oq-gs-builder.sh populate "$oqpdir" "$oqpdir" "${oqpdir}/bin" "$GEM_GS_WS_NAME" "$GEM_GS_DS_NAME" "$gem_db_name" "$gem_db_user" "$gem_db_pass" "${GEM_GS_DATADIR}" "${GEM_APP_LIST[@]}"
    ${oqpdir}/bin/oq-gs-builder.sh populate -a $HOME/oq-private/output "openquakeplatform/" "openquakeplatform/" "openquakeplatform/bin" "oqplatform" "oqplatform" "$gem_db_name" "$gem_db_user" "$gem_db_pass" "geoserver/data"

    # if [ "$GEM_IS_INSTALL" == "y" ]; then
    #     openquakeplatform updatelayers

    #     #
    #     #  post layers creation apps customizations
    #     #  FIXME this must be run also on NEW applications (if any exists) during upgrades;
    #     #        OLD applications that changed should use migrations and must be skipped here
    #     for app in "${GEM_APP_LIST[@]}"; do
    #         if function_exists "${app}_postlayers"; then
    #             "${app}_postlayers" "$oqpdir" "$gem_db_name"
    #         fi
    #     done
    # fi

    chown -R www-data.www-data /var/www/openquake

    if [ ! -d "$MIGRATIONS_HISTORY" ]; then
        mkdir -p "$MIGRATIONS_HISTORY"
    fi
    find oq-platform2/openquakeplatform/migrations -type f \( -name "*.py" -or -name "*.sql" -or -name "*.sh" \) -exec cp "{}" "${MIGRATIONS_HISTORY}/" \;

    if [ "$gem_oq_bing_key" != "" ]; then
        echo "UPDATE maps_maplayer SET source_params = regexp_replace(source_params, '\"ptype\": \"gxp_bingsource\"',
     '\"apiKey\": \"$gem_oq_bing_key\", \"ptype\": \"gxp_bingsource\"')
     WHERE  name = 'AerialWithLabels' AND source_params NOT LIKE '%\"apiKey\":%'; " | sudo -u postgres psql -e "$gem_db_name"
    else
        echo "DELETE FROM maps_maplayer WHERE NAME = 'AerialWithLabels';" | sudo -u postgres psql -e "$gem_db_name"
    fi

    if [ "$GEM_IS_INSTALL" == "y" ]; then
        # updatelayers must be run again after the fixtures have been pushed
        # to allow synchronization of keywords and metadata from GN to GS
        openquakeplatform updatelayers
    else
        # the updatelayers is very expensive during upgrades due the number of layers
        # that could be hosted in the Platform. Let the user run it in a convinient way for him,
        # i.e. in background, avoiding a long downtime.
        echo "WARNING: please run 'sudo openquakeplatform updatelayers' to complete the upgrade."
        echo "         The 'updatelayers' process could be very expensive in matter of time, IO and CPU"
        echo "         depending on the number of layers hosted by the Platform. It can be run in background."
    fi

}

usage() {
    local com="$1" ret="$2"
    echo "${com} <--help|-p> <--hostname|-H> hostname [<--db_name|-d> db_name] [<--db_user|-u> db_user] [<--webuiurl|-w> <addr>] [<--oq_engserv_key|-k> <key>] [<--oq_bing_key|-B> <bing-key>]"
    exit $ret
}

#
#  MAIN
#

# check the current path
# fil_inode="$(ls -i "$0" | cut -d ' ' -f 1)"
# ext_inode="$(ls -i "$PWD/oq-platform2/openquakeplatform/bin/deploy.sh" 2>/dev/null | cut -d ' ' -f 1)"
# 
# if [ "$fil_inode" != "$ext_inode" ]; then
#     echo "  This script must be run from the parent directory of oq-platform repository."
#     echo "  Change the current directory and run ./oq-platform2/openquakeplatform/bin/deploy.sh script again."
#     exit 1
# fi

wai="$(whoami)"

if [ "$wai" = "root" ]; then
    parsargs "norm_user|U:,norm_dir|D:,help|p,hostname|H:,db_name|d:,db_user|u:,webuiurl|w:,oq_engserv_key|k:,oq_bing_key|B:" "$@"
    if [ "${globargs['hostname']}" == "" ]; then
        usage "$0" 1
    fi

    oq_platform_install
    exit $?
else
    parsargs "help|p,hostname|H:,db_name|d:,db_user|u:,webuiurl|w:,oq_engserv_key|k:,oq_bing_key|B:" "$@"

    if [ "${globargs['hostname']}" == "" -o "${globargs['help']}" ]; then
        usage "$0" 1
    fi

    echo "You are running the openquake platform installation script."
    echo
    echo "During this operation some git repositories will be downloaded into the current"
    echo "directory $PWD"
    echo
    read -p "press ENTER to continue or CTRL+C to abort:" a
    echo
    sudo -p "To install openquake platform root permissions are required.${NL}Please type password for $wai: " GEM_SET_DEBUG=$GEM_SET_DEBUG $0 --norm_user="$wai" --norm_dir="$PWD" "$@"
    exit $?
fi
