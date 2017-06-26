#!/usr/bin/env python
import os
import unittest
from openquakeplatform.test import pla
from selenium.webdriver.common.keys import Keys


class TermsTest(unittest.TestCase):

    def terms_test(self):

        pla.get('')

        # terms of use
        ter = pla.xpath_finduniq(
            "//a[normalize-space(text())='Terms of use']",
            100, 1)
        ter.click()

        pla.wait_new_page(ter, '/account/terms', timeout=10)

        #search title page
        pla.xpath_finduniq(
            "//h1[normalize-space(text())='Terms of use']")
