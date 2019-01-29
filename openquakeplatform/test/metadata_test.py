#!/usr/bin/env python
import unittest
import time
from openquake.moon import platform_get


# try download metadata from some layer
def download_meta(self):

    pla = platform_get()

    pla.get('/layers')

    # click on layer ghec
    layer = pla.xpath_finduniq(
        "//a[normalize-space(text()) = 'ghec_viewer_measure']")
    layer.click()

    # click download metadata in layer page detail ghec
    download_meta = pla.xpath_finduniq(
        "//button[@data-target = '#download-metadata']")
    download_meta.click()

    # click standard metadata ghec
    standard_meta = pla.xpath_finduniq(
        "//a[normalize-space(text()) = 'Dublin Core']")
    standard_meta.click()

    time.sleep(2)


class MetadataTest(unittest.TestCase):

    def check_metadata_test(self):

        pla = platform_get()

        download_meta(self)

        # switch window tab
        window_after = pla.driver.window_handles[1]
        pla.driver.switch_to.window(window_after)

        # if do login is not localhost
        try:
            # login
            user = pla.xpath_findfirst(
                "//input[@id = 'id_username']")
            user.send_keys('admin')

            pwd = pla.xpath_findfirst(
                "//input[@id = 'id_password']")
            pwd.send_keys('admin')

            login = pla.xpath_finduniq(
                "//button[normalize-space(text())='Log in']")
            login.click()
        except:
            raise ValueError('Cannot do login')

        # close tab and return to main window
        # pla.windows_reset()

        download_meta(self)

        pla.driver.window_handles[0]
