#!/usr/bin/env python
import unittest
from openquakeplatform.test import pla


class AppVersionsTest(unittest.TestCase):

    def page_app_versions_test(self):

        versions_url = '/versions'

        # redirect page of versions application
        pla.get(versions_url)

        pla.xpath_finduniq(
            "//h2[@class='page-title'"
            " and normalize-space(text())='Application Versions']")
