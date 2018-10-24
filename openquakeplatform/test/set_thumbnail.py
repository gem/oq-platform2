#!/usr/bin/env python
import os
import unittest
from openquake.moon import platform_get

TIMEOUT = 100


class SetThumbsTest(unittest.TestCase):

    def set_thumbs_map_test(self):

        pla = platform_get()

        pla.get('/maps/')
        # New window with platform without login
        plb = pla.platform_create(user='admin', passwd='admin')

        # plb.init(landing='/maps/')

        maps = pla.driver.find_elements_by_xpath(
            "//a[@class='oq-map ng-binding ng-scope']")
        # "//a[@class='ng-binding']")
        print(maps)

        for links in maps:
            link = links.get_attribute("href")
            href_map = os.path.basename(link)
            plb.init(landing='/maps/%s' % href_map, autologin=True)

            # Click edit map
            edit_map_button = plb.xpath_finduniq(
                "//button[@data-target='#edit-map'"
                "and normalize-space(text())='Edit Map']",
                100, 1)
            edit_map_button.click()

            # Click set thumbnail
            edit_thumb = plb.xpath_finduniq(
                "//a[@id='set_thumbnail'"
                "and normalize-space(text())='Set']",
                100, 1)
            edit_thumb.click()

            plb.window_close()

        # href = maps.get_attribute('href')
        # href_map = os.path.basename(href)
        # print(href_map)
        # for link in href_map:
        #     print(link)
        #     pla.get("/maps/%s" % link)
