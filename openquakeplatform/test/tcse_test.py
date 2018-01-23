#!/usr/bin/env python
import unittest
from openquake.moon import platform_get


class TcseTest(unittest.TestCase):

    def calculate_test(self):

        pla = platform_get()

        # calculate
        cal = pla.xpath_finduniq(
            "//a[normalize-space(text())='Calculate']",
            100, 1)
        cal.click()

        pla.wait_new_page(cal, '/calculate', timeout=10)

        # search title page
        pla.xpath_finduniq(
            "//h1[normalize-space(text())='OpenQuake Calculate']")

    def explore_test(self):

        pla = platform_get()

        # calculate
        exp = pla.xpath_finduniq(
            "//a[normalize-space(text())='Explore']",
            100, 1)
        exp.click()

        pla.wait_new_page(exp, '/explore', timeout=10)

        # search title page
        pla.xpath_finduniq(
            "//h1[normalize-space(text())='OpenQuake Explore']")

    def share_test(self):

        pla = platform_get()

        # calculate
        sha = pla.xpath_finduniq(
            "//a[normalize-space(text())='Share']",
            100, 1)
        sha.click()

        pla.wait_new_page(sha, '/share', timeout=10)

        # search title page
        pla.xpath_finduniq(
            "//h1[normalize-space(text())='OpenQuake Share']")

    def terms_test(self):

        pla = platform_get()

        pla.get('')

        # terms of use
        ter = pla.xpath_finduniq(
            "//a[normalize-space(text())='Terms of use']",
            100, 1)
        ter.click()

        pla.wait_new_page(ter, '/account/terms', timeout=10)

        # search title page
        pla.xpath_finduniq(
            "//h1[normalize-space(text())='Terms of use']")
