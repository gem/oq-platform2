from openquake.moon import platform_get, platform_del


def setup_package():
    pla = platform_get()
    pla.init(timeout=100)


def teardown_package():
    platform_del()
