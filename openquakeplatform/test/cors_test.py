#!/usr/bin/env python
import unittest
import os
from openquake.moon import platform_get


class CorsTest(unittest.TestCase):
    def cors_test(self):

        pla = platform_get()

        exp_page = (
            "/taxtweb/explanation/DX+D99/"
            "S+S99+BOL/LWAL+DU99/DY+D99/"
            "S+S99+BOL/LWAL+DU99/H99/Y99/"
            "OC99/BP99/PLF99/IR99/EW99/"
            "RSH99+RMT99+R99+RWC99/"
            "F99+FWC99/FOS99"
        )

        pla.get(exp_page)

        # pla.wait_new_page(exp_page_get, exp_page)
