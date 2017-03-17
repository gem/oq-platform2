import time
import sys
import nose

from openquake.moon import Moon

# uncomment to run pdb when untrapped exception is raised
#
# from IPython.core import ultratb
# sys.excepthook = ultratb.FormattedTB(mode='Verbose',
#      color_scheme='Linux', call_pdb=1)


pla = Moon(jqheavy=True)
pla.primary_set()


def setup_package():
    pla.init()


def teardown_package():
    pla.fini()
