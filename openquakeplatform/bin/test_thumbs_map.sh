#!/bin/bash
GEM_GIT_REPO="https://github.com/gem"
GIT_REPO="oq-platform2"
HOST="$1"
PASSWD="$2"
function initialize_test() {
    #install selenium,pip,geckodriver,clone oq-moon and execute tests with nose
    sudo apt-get -y install python-pip wget
    pip install --upgrade pip
    pip install nose
    wget "http://ftp.openquake.org/common/selenium-deps"
    GEM_FIREFOX_VERSION="$(dpkg-query --show -f '${Version}' firefox)"
    . selenium-deps
    wget "http://ftp.openquake.org/mirror/mozilla/geckodriver-v${GEM_GECKODRIVER_VERSION}-linux64.tar.gz"
    tar zxvf "geckodriver-v${GEM_GECKODRIVER_VERSION}-linux64.tar.gz"
    sudo cp geckodriver /usr/local/bin
    pip install -U selenium==${GEM_SELENIUM_VERSION}
    git clone $GEM_GIT_REPO/oq-moon.git

    cp $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py.tmpl $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py
    cp $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py.tmpl $GIT_REPO/openquakeplatform/set_thumb/moon_config.py

    sed -i 's/localhost:8000/'"$HOST"'/g' $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py
    sed -i 's/localhost:8000/'"$HOST"'/g' $HOME/$GIT_REPO/openquakeplatform/set_thumb/moon_config.py

    sed -i 's/pla_passwd = "admin"/pla_passwd = "'"$PassWD"'"/g' $HOME/$GIT_REPO/openquakeplatform/test/config/moon_config.py
    sed -i 's/pla_passwd = "admin"/pla_passwd = "'"$PassWD"'"/g' $HOME/$GIT_REPO/openquakeplatform/set_thumb/moon_config.py

    export PYTHONPATH=$HOME/oq-moon:$HOME/$GIT_REPO:$HOME/$GIT_REPO/openquakeplatform/test/config:$HOME/oq-platform-taxtweb:$HOME/oq-platform-ipt:$HOME/oq-platform-building-class
}

function exec_set_map_thumbs() {
    export DISPLAY=:1
    python -m openquake.moon.nose_runner --failurecatcher dev -s -v --with-xunit --xunit-file=xunit-platform-dev.xml $GIT_REPO/openquakeplatform/set_thumb/mapthumbnail_test.py
}

initialize_test
exec_set_map_thumbs
