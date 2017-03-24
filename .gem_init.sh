export GEM_SET_DEBUG=true
if [ "" = "true" ]; then
    export OQ_MOON_STATS=
fi

set -e
if [ -n "$GEM_SET_DEBUG" -a "$GEM_SET_DEBUG" != "false" ]; then
    export PS4='+${BASH_SOURCE}:${LINENO}:${FUNCNAME[0]}: '
    set -x
fi
source .gem_ffox_init.sh
