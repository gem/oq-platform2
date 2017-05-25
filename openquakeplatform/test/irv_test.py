#!/usr/bin/env python
import unittest

from openquakeplatform.test import pla

@unittest.skip("temporarily disabled")
class IrvTest(unittest.TestCase):
    def irv_test(self):
        # go to test page
        pla.get('/irv/test/')

        # wait DOM population via async JS
        pla.xpath_finduniq(
            "//div[@class='jasmine_html-reporter']/div"
            "[@class='results']/div[@class='summary']",
            100, 1)

        # check the result of tests
        pla.xpath_finduniq(
            "//span[@class='bar passed' and contains"
            "(normalize-space(text()), ', 0 failures')]")