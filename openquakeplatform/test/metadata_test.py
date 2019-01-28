#!/usr/bin/env python
import unittest
from openquake.moon import platform_get


class MetadataTest(unittest.TestCase):

    def check_metadata_test(self):

        pla = platform_get()

        # gem_user = 'GEM'
        # gem_pwd = 'GEM'

        # # New window with platform without other login
        # plb = pla.platform_create(user=None, passwd=None)
        # plb.init(landing='/', autologin=False)
        #
        # # New login
        # signin = plb.xpath_finduniq("//a[normalize-space(text()) = 'Sign in']")
        # signin.click()

        pla.get('/layers')

        # click on layer
        layer = pla.xpath_finduniq(
            "//a[normalize-space(text()) = 'ghec_viewer_measure']")
        layer.click()

        # click download metadata in layer page detail
        download_meta = pla.xpath_finduniq(
            "//button[@data-target = '#download-metadata']")
        download_meta.click()

        # click standard metadata
        standard_meta = pla.xpath_finduniq(
            "//a[normalize-space(text()) = 'Dublin Core']")
        standard_meta.click()

        # import time
        # time.sleep(5000000)

        import time
        time.sleep(2)

        window_after = pla.driver.window_handles[1]

        page_meta = pla.driver.switch_to.window(window_after)

        print(window_after)
        print(page_meta)

        # check metadata page
        pla.wait_new_page(
            page_meta, 'http://localhost:8000/catalogue/csw?outputschema'
            '=http%3A%2F%2Fwww.opengis.net%2Fcat%2Fcsw%2F2.0.2&service'
            '=CSW&request=GetRecordById&version=2.0.2&elementsetname='
            'full&id=4b9fc50b-7dae-4839-a2d0-2f62121da2d8', timeout=10)
