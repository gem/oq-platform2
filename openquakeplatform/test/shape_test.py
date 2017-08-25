#!/usr/bin/env python
import os
import unittest
from openquakeplatform.test import pla
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class ShapeTest(unittest.TestCase):

    def upload_shape_test(self):

        pla.get('')

        # layers in homepage
        linklayer = pla.xpath_finduniq(
            "//a[normalize-space(text())='Layers' and @role='button']",
            100, 1)
        linklayer.click()

        pla.wait_new_page(linklayer, '/layers/?limit=100&offset=0', timeout=10)

        # upload layers
        uploadlayer = pla.xpath_finduniq(
            "//a[normalize-space(text())='Upload Layers']",
            100, 1)
        uploadlayer.click()

        pla.wait_new_page(uploadlayer, '/layers/upload', timeout=10)

        # choose shape file
        sph = os.path.join(os.path.expanduser("~"), 'oq-platform2',
                                                    'openquakeplatform',
                                                    'test',
                                                    'shapefile',
                                                    'exampleshape.zip')
        import pdb ; pdb.set_trace()

        chooselayer = pla.xpath_finduniq(
             "//input[@type='file'and @id='file-input']",
             100, 1)
        chooselayer.send_keys(sph)

        # confirm upload layers
        confuplayer = pla.xpath_finduniq(
            "//a[normalize-space(text())='Upload files']",
            100, 1)
        confuplayer.send_keys(Keys.ENTER)

        # success load layer
        pla.xpath_finduniq(
            "//p[normalize-space(text())='Your layer was successfully"
            " uploaded']",
            100, 1)

        succuploadlayer = pla.xpath_finduniq(
             "//a[normalize-space(text())='Layer Info']",
             100, 1)
        succuploadlayer.click()

        # page where exist layer create
        pla.wait_new_page(succuploadlayer, '/layers/geonode:exampleshape',
                          timeout=20)
        pla.get('')

        # layers in homepage
        linklayertwo = pla.xpath_finduniq(
            "//a[normalize-space(text())='Layers' and @role='button']",
            100, 1)
        linklayertwo.click()

        pla.wait_new_page(linklayertwo, '/layers', timeout=10)

        # click on title shapefile inserted
        lay = pla.xpath_finduniq(
            "//a[normalize-space(text())='exampleshape' and"
            " @class='ng-binding']",
            100, 1)
        lay.click()

        # page where exist layer create
        pla.wait_new_page(lay, '/layers/geonode:exampleshape',
                          timeout=20)

        # click edit layer

        editbutton = pla.xpath_finduniq(
            "//button[normalize-space(text())='Edit Layer' and"
            " @data-target='#edit-layer']",
            100, 1)

        editbutton.send_keys(Keys.ENTER)

        # click remove
        removebutton = pla.xpath_finduniq(
            "//a[normalize-space(text())='Remove']",
            100, 1)

        removebutton.click()

        # wait if the page for confirm exist
        pla.wait_new_page(removebutton, '/layers/geonode:exampleshape/remove',
                          timeout=20)

        # click button for confirm
        confsure = pla.xpath_finduniq(
            "//input[normalize-space(@value)='Yes, I am sure' and"
            " @type='submit']",
            100, 1)
        confsure.click()

        pla.get('')

        # layers in homepage
        newlinklayer = pla.xpath_finduniq(
            "//a[normalize-space(text())='Layers' and @role='button']",
            100, 1)
        newlinklayer.click()

        # check if page list layers
        pla.wait_new_page(newlinklayer, '/layers', timeout=20)

        # search exampleshape and if found go to error
        try:
            pla.xpath_finduniq(
                "//a[normalize-space(text())='exampleshape' and"
                " @class='ng-binding']",
                timeout=5.0)
        except:
            pass
        else:
            self.assertFalse(False, msg="exampleshape deleted layer founded")
