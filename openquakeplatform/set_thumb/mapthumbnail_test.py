#!/usr/bin/env python
import os
import unittest
import time
from openquake.moon import platform_get

TIMEOUT = 100


class SetThumbsTest(unittest.TestCase):

    def set_thumbs_map_test(self):

        pla = platform_get()

        pla.get('/maps/?limit=200&offset=0')

        time.sleep(5)

        maps = pla.driver.find_elements_by_xpath(
            "//a[@class='oq-map ng-binding ng-scope']")

        links = []
        for map_item in maps:
            link = map_item.get_attribute("href")
            links.append(os.path.basename(link))

        for link_meta in links:

            pla.get('/maps/%s' % link_meta)

            time.sleep(5)

            # Click edit map
            edit_map_button_meta = pla.xpath_finduniq(
                "//button[@data-target='#edit-map'"
                " and normalize-space(text())='Edit Map']",
                TIMEOUT, 1)
            edit_map_button_meta.click()

            edit_meta = pla.xpath_finduniq(
                "//a[@href='/maps/%s/metadata'"
                " and normalize-space(text())='Edit']" % link_meta,
                TIMEOUT, 1)
            edit_meta.click()

            # Click update metadata
            update_button_meta = pla.xpath_findfirst(
                "//input[@type='submit' and @value='Update']",
                TIMEOUT, 1)
            update_button_meta.click()

            print('Refreshed Metadata for map with id: %s' % link_meta)

        for link in links:
            pla.get('/maps/%s' % link)

            time.sleep(3)

            # Click edit map
            edit_map_button = pla.xpath_finduniq(
                "//button[@data-target='#edit-map'"
                " and normalize-space(text())='Edit Map']",
                TIMEOUT, 1)
            edit_map_button.click()

            # Click set thumbnail
            edit_thumb = pla.xpath_finduniq(
                "//a[@id='set_thumbnail'"
                " and normalize-space(text())='Set']",
                TIMEOUT, 1)
            edit_thumb.click()

            print('Set thumbnail for map with id: %s' % link)
