mport os
import unittest
from openquakeplatform.test import pla
from selenium.webdriver.common.keys import Keys


class CseTest(unittest.TestCase):

    def calculate_test(self):

        #pla.get('')

        # calculate
        cal = pla.xpath_finduniq(
            "//a[normalize-space(text())='Calculate']",
            100, 1)
        cal.click()

        pla.wait_new_page(cal, '/calculate', timeout=10)

        #search title page
        pla.xpath_finduniq(
            "//h1[normalize-space(text())='OpenQuake Calculate']")

    def explore_test(self):

        # calculate
        exp = pla.xpath_finduniq(
            "//a[normalize-space(text())='Explore']",
            100, 1)
        exp.click()

        pla.wait_new_page(exp, '/explore', timeout=10)

        #search title page
        pla.xpath_finduniq(
            "//h1[normalize-space(text())='OpenQuake Explore']")

    def share_test(self):

        # calculate
        sha = pla.xpath_finduniq(
            "//a[normalize-space(text())='Share']",
            100, 1)
        sha.click()

        pla.wait_new_page(sha, '/share', timeout=10)

        #search title page
        pla.xpath_finduniq(
            "//h1[normalize-space(text())='OpenQuake Share']")
