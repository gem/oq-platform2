#!/usr/bin/env python
import unittest
from openquake.moon import platform_get

TIMEOUT = 100


class MapsTest(unittest.TestCase):

    def new_map_page_no_login_test(self):

        pla = platform_get()

        # New window with platform without login
        plb = pla.platform_create(user=None, passwd=None)
        plb.init(landing='/', autologin=False)

        # To visualize maps list
        list_maps = plb.xpath_finduniq(
            "//a[@href='/maps/' and @class='oq-button-home-btn btn']", TIMEOUT)
        list_maps.click()

        # Create new map
        create_new_map = plb.xpath_finduniq(
            "//a[@href='/maps/new' and"
            " @class='btn btn-primary pull-right']", TIMEOUT)
        create_new_map.click()

        # Check page new map
        plb.wait_new_page(create_new_map, '/maps/new', timeout=10)

        # Check warning must login
        plb.xpath_finduniq(
            "//div[@class='map_warning']", TIMEOUT)

        pla.platform_destroy(plb)
