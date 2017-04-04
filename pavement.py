import os

from setuptools.command import easy_install
from urlparse import urlparse

from paver.easy import task, options, cmdopts, needs
from paver.easy import path, sh, info, call_task
from paver.easy import BuildFailure


GEM_LOCAL_SETTINGS_TMPL = 'local_settings.py.tmpl'


def _write_local_settings(lxc_ip, webuiurl, datadir):
    local_settings = open(GEM_LOCAL_SETTINGS_TMPL, 'r').read()
    with open(os.path.join(os.path.expanduser("~"), 'oq-platform2'
                                                    'openquakeplatform'
                                                    'local_settings'
                                                    '.py'), 'w') as fh:
        fh.write(local_settings % dict(lxc_ip=lxc_ip,
                                       webuiurl=webuiurl,
                                       datadir=datadir
                                       ))


@task
@cmdopts([
    ('lxc_ip=', 'l', 'Bind server to provided IP address and port number.'),
    ('webuiurl=', 'u', 'Bind server to provided URL of webui.')
    ('datadir=', 'd', 'Value for FILE_PATH_FIELD_DIRECTORY in ipt')
])
def setup():
    lxc_ip = options.get('lxc_ip', '')
    webuiurl = options.get('webuiurl', '')
    datadir = options.get('datadir', '')
    # info(lxc_ip)
    _write_local_settings(lxc_ip, webuiurl, datadir)
    info("Local setting changed.")


