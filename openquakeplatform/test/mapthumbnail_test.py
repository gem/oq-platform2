#!/usr/bin/env python
import os
import unittest
from openquake.moon import platform_get

TIMEOUT = 100


class SetThumbsTest(unittest.TestCase):

    def set_thumbs_map_test(self):

        pla = platform_get()

        pla.get('/maps/')

        maps = pla.driver.find_elements_by_xpath(
            "//a[@class='oq-map ng-binding ng-scope']")

        links = []
        for map_item in maps:
            link = map_item.get_attribute("href")
            links.append(os.path.basename(link))

        for link in links:
            pla.get('/maps/%s' % link)

            # Click edit map
            edit_map_button = pla.xpath_finduniq(
                "//button[@data-target='#edit-map'"
                "and normalize-space(text())='Edit Map']",
                TIMEOUT, 1)
            edit_map_button.click()

            # Click set thumbnail
            edit_thumb = pla.xpath_finduniq(
                "//a[@id='set_thumbnail'"
                "and normalize-space(text())='Set']",
                TIMEOUT, 1)
            edit_thumb.click()
