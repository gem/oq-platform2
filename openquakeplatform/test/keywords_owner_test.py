#!/usr/bin/env python
import unittest
import time
from openquake.moon import platform_get

TIMEOUT = 100


class SetMetadataKeywordsOwnerTest(unittest.TestCase):

    def new_metadata_owner_test(self):

        pla = platform_get()

        new_owner = '%s' % ('admin')

        pla.get('/documents/?limit=200&offset=0')

        time.sleep(2)

        document = pla.xpath_finduniq(
            "//a[normalize-space(text()) = 'Global "
            "Strain Rate Model - Final Report']")

        document.click()

        # Click edit map
        edit_doc_button_meta = pla.xpath_finduniq(
            "//button[@data-target='#edit-document'"
            " and normalize-space(text())='Edit Document']",
            TIMEOUT, 1)
        edit_doc_button_meta.click()

        # Click edit metadata
        edit_meta = pla.xpath_finduniq(
            "//a[normalize-space(text())='Edit']", TIMEOUT, 1)
        edit_meta.click()

        # Change owner
        remove_owner = pla.xpath_findfirst(
            "//span[@class='remove']", TIMEOUT, 1)
        remove_owner.click()

        # edit owner
        edit_owner_field = pla.xpath_finduniq(
            "//input[@id='id_resource-owner-autocomplete']", TIMEOUT, 1)
        edit_owner_field.send_keys('%s' % new_owner)

        time.sleep(5000000000)

        choose_owner_field = pla.xpath_finduniq(
            "//span[@class='yourlabs-autocomplete autocomplete-light-widget']",
            "/span[normalize-space(text())='admin']", TIMEOUT, 1)
        choose_owner_field.click()

        # choose name
        choose_owner_field = pla.xpath_finduniq(
            "//span[normalize-space(text())='admin']", TIMEOUT, 1)
        choose_owner_field.click()

        # Click update metadata
        update_button_meta = pla.xpath_findfirst(
            "//input[@type='submit' and @value='Update']",
            TIMEOUT, 1)
        update_button_meta.click()

        # pla.wait_new_page(update_button_meta, '/documents/', timeout=10)

        # check new owner
        pla.xpath_finduniq(
            "//a[@itemprop='author' and "
            "normalize-space(text())='admin'", TIMEOUT, 1)
