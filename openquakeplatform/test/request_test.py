#!/usr/bin/env python
import unittest

from openquake.moon import platform_get


class RequestTest(unittest.TestCase):
    def request_test(self):

        pla = platform_get()

        # go to test page
        pla.get('/admin')

        # click requests
        click_req = pla.xpath_finduniq(
            "//a[@href='/admin/request/request/'"
            " and normalize-space(text())='Requests']",
            100, 1)
        click_req.click()

        # check title in requests list page
        pla.xpath_finduniq(
            "//h1[normalize-space(text())='Select request to change']",
            100, 1)

        # click overview
        overview = pla.xpath_finduniq(
            "//a[@href='/admin/request/request/overview/'"
            " and normalize-space(text())='Overview']",
            100, 1)
        overview.click()

        # check page overview
        pla.wait_new_page(
            overview, '/admin/request/request/overview', timeout=5)

        # check title in requests overview page
        pla.xpath_finduniq(
            "//h1[normalize-space(text())='Request overview']",
            100, 1)
