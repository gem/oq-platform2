GEM_LOCAL_SETTINGS_TMPL = 'geonode/geonode/local_settings.py.template'
def _write_local_settings(lxc_ip):
    local_settings = open(GEM_LOCAL_SETTINGS_TMPL, 'r').read()
    with open('geonode/geonode/local_settings.py', 'w') as fh:
        fh.write(local_settings % dict(lxc_ip=lxc_ip))
