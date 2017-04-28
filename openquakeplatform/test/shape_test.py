#!/usr/bin/env python
import unittest

from openquakeplatform.test import pla

# from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.keys import Keys


class ShapeTest(unittest.TestCase):

    def upload_shape_test(self):

        sph = "~/oq-platform2/openquakeplatform/test/shapefile/exampleshape.zip"

        pla.get('')

        # layers in homepage
        linklayer = pla.xpath_finduniq(
            "//a[normalize-space(text())='Layers' and @role='button']",
            100, 1)
        linklayer.click()

        pla.wait_new_page(linklayer, '/layers', timeout=10)

        # upload layers
        uploadlayer = pla.xpath_finduniq(
            "//a[normalize-space(text())='Upload Layers']",
            100, 1)
        uploadlayer.click()

        pla.wait_new_page(uploadlayer, '/layers/upload', timeout=10)

        # choose shape file
        chooselayer = pla.xpath_finduniq(
             "//input[@type='file'and @id='file-input']",
             100, 1)
        chooselayer.send_keys(sph)

        # confirm upload layers
        confuplayer = pla.xpath_finduniq(
            "//a[normalize-space(text())='Upload files']",
            100, 1)
        confuplayer.send_keys(Keys.ENTER)
        confuplayer.click()

        # success load layer
        pla.xpath_finduniq(
            "//p[normalize-space(text())='Your layer was successfully"
            " uploaded']")

        succuploadlayer = pla.xpath_finduniq(
             "//a[normalize-space(text())='Layer Info']",
             100, 1)

        succuploadlayer.click()

        # page where exist layer create
        # pla.wait_new_page(succuploadlayer, '/layers/geonode:exampleshape',
        #                   timeout=20)

        # pla.get('')
