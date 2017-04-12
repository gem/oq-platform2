        import os

from setuptools.command import easy_install
from urlparse import urlparse

from paver.easy import task, options, cmdopts, needs
from paver.easy import path, sh, info, call_task
from paver.easy import BuildFailure


GEM_LOCAL_SETTINGS_TMPL = 'local_settings.py.tmpl'


def _write_local_settings(lxc_ip, webuiurl, db_name, db_user, db_pass):
    local_settings = open(GEM_LOCAL_SETTINGS_TMPL, 'r').read()
    with open(os.path.join(os.path.expanduser("~"), 'geonode/geonode/'
                                                    'local_settings'
                                                    '.py'), 'w') as fh:
        fh.write(local_settings % dict(lxc_ip=lxc_ip,
                                       webuiurl=webuiurl,
                                       db_name=db_name,
                                       db_user=db_user,
                                       db_pass=db_pass,
                                       ))


@task
@cmdopts([
    ('lxc_ip=', 'l', 'Bind server to provided IP address and port number.'),
    ('webuiurl=', 'u', 'Bind server to provided URL of webui.')
])
def setup():
    lxc_ip = options.get('lxc_ip', '')
    webuiurl = options.get('webuiurl', '')
    db_name = "geonode_dev"
    db_user = "geonode_dev"
    db_pass = "geonode_dev"
    # info(lxc_ip)
    _write_local_settings(lxc_ip, webuiurl, db_name, db_user, db_pass)
    info("Local setting changed.")


