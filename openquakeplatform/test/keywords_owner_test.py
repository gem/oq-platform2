#!/usr/bin/env python
import os
import unittest
import time
from openquake.moon import platform_get

TIMEOUT = 100


class SetMetadataKeywordsOwnerTest(unittest.TestCase):

    def new_metadata_owner_test(self):

        pla = platform_get()

        pla.get('/documents/?limit=200&offset=0')

        time.sleep(2)

        document = pla.xpath_finduniq(
            "//a[normalize-space(text()) = 'Global "
            "Strain Rate Model - Final Report")

        document.click()

        # Click edit map
        edit_doc_button_meta = pla.xpath_finduniq(
            "//button[@data-target='#edit-document'"
            " and normalize-space(text())='Edit Document']",
            TIMEOUT, 1)
        edit_doc_button_meta.click()

        edit_meta = pla.xpath_finduniq(
            "//a[normalize-space(text())='Edit']", TIMEOUT, 1)
        edit_meta.click()
