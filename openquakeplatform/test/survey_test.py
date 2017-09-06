#!/usr/bin/env python
import os
import unittest
from openquakeplatform.test import pla
from selenium.webdriver.common.keys import Keys


class SurveyTest(unittest.TestCase):

    def watch_tut_test(self):

        # calculate
        wat = pla.xpath_finduniq(
            "//a[normalize-space(text())='watch tutorial here']",
            100, 1)
        wat.click()

        pla.wait_new_page(wat, '/building-class/tutorial', timeout=10)
