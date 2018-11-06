import os
import unittest
from openquake.moon import platform_get


class landing_test(unittest.TestCase):

    def diff_landing_test(self):

        pla = platform_get()
        pla.get('')
        # New window with platform without login
        plb = pla.platform_create(user='admin', passwd='admin')

        plb.init(landing='/maps/?limit=100&offset=0', autologin=True)
