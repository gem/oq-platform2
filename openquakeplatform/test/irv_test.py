#!/usr/bin/env python
import unittest

from openquake.moon import platform_get


class IrvTest(unittest.TestCase):
    def irv_test(self):

        pla = platform_get()

        # go to test page
        pla.get('/irv')

        # check map     
        pla.xpath_finduniq(
            "//div[@id='map' and @class='mapboxgl-map']",
            100, 1)
