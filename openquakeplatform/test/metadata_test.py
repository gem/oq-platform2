#!/usr/bin/env python

##### with this test we can check if pycsw works
##### and if catalogue is correctly setted in local settings

import unittest
import time
import os
import socket
from openquake.moon import platform_get


class MetadataTest(unittest.TestCase):

    def check_metadata_test(self):

        # check ip adress
        get_ip = os.environ("LXC_IP")

        print('Get_ip: %s' % get_ip)

        pla = platform_get()

        pla.get('/layers')

        # click on layer ghec
        layer = pla.xpath_finduniq(
            "//a[normalize-space(text()) = 'ghec_viewer_measure']")
        layer.click()

        # click download metadata in layer page detail
        download_meta = pla.xpath_finduniq(
            "//button[@data-target = '#download-metadata']")
        download_meta.click()

        # click standard metadata ghec
        standard_meta = pla.xpath_finduniq(
            "//a[normalize-space(text()) = 'Dublin Core']")
        standard_meta.click()

        time.sleep(2)

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

        pla.driver.window_handles[1]

        pla.wait_new_page(
                login, 'http://%s:8000/catalogue/csw' % get_ip)

        # close window and swith to previous window
        pla.window_close()
        window_before = pla.driver.window_handles[0]
        pla.driver.switch_to.window(window_before)

