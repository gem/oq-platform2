#!/usr/bin/env python
import unittest
from openquake.moon import platform_get


class AppVersionsTest(unittest.TestCase):

    def page_app_versions_test(self):

        pla = platform_get()

        versions_url = '/versions'

        # redirect page of versions application
        pla.get(versions_url)

        pla.xpath_finduniq(
            "//h1[normalize-space(text())='Versions']")

        # macthing if the version of applications
        # content numbers and points
        search_version_app = pla.xpath_finduniq(
            "//table[@class='versions_table']//tr/"
            "td[../td[normalize-space(text())"
            "='IPT']][normalize-space(text())!='IPT']")
        vers = search_version_app.text
        self.assertRegexpMatches(vers, '^[0-9]+\.', msg=(
            "version [%s] not valid for IPT app" % vers))
