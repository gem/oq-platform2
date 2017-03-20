import os
#import re
#import shutil
#import sys
#import time
#import urllib
#import urllib2
#import zipfile
#import glob
#import fileinput
#import yaml

from setuptools.command import easy_install
from urlparse import urlparse

from paver.easy import task, options, cmdopts, needs
from paver.easy import path, sh, info, call_task
from paver.easy import BuildFailure


GEM_LOCAL_SETTINGS_TMPL = os.path.join(os.path.expanduser("~"),
                                           'geonode/geonode', 
                                           'local_settings.py.tmpl')

#GEM_LOCAL_SETTINGS_TMPL = 'geonode/geonode/local_settings.py.tmpl'
def _write_local_settings(lxc_ip):
    local_settings = open(GEM_LOCAL_SETTINGS_TMPL, 'r').read()
    with open(os.path.join(os.path.expanduser("~"), 'geonode/geonode',
                               'local_settings.py.tmpl'), 'w') as fh:
        fh.write(local_settings % dict(lxc_ip=lxc_ip
                                       ))

@task
@cmdopts([
    ('lxc_ip=', 'l', 'Bind server to provided IP address and port number.')
])
def setup():
    lxc_ip = options.get('lxc_ip', '')
    # info(lxc_ip)
    _write_local_settings(lxc_ip)
    info("Local setting changed.")

