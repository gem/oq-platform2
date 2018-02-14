#!/usr/bin/env python
import unittest
from openquake.moon import platform_get


class HazusTest(unittest.TestCase):

    def exist_page_test(self):

        pla = platform_get()

        pla.get('/hazus')

        # search select element
        pla.xpath_finduniq(
            "//select[@id='external-layers-menu']")
