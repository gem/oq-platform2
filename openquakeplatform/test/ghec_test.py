#!/usr/bin/env python
import unittest
import os
from openquake.moon import platform_get


class GhecTest(unittest.TestCase):
    def ghec_test(self):

        pla = platform_get()

        pla.get('/explore')
        pla.wait_new_page("//b[contains(text(),"
                          " 'Seismic Hazard Data Sets and Models')]",
                          "/explore", strategy="next", timeout=10)

        # <li>
        # <a href="/maps/23">
        enter_button = pla.xpath_finduniq(
            "//li/a[normalize-space(text()) = 'Global "
            "Historical Earthquake Catalogue "
            "and Archive (1000-1903)']")

        href = enter_button.get_attribute('href')
        id_map = os.path.basename(href)
        enter_button.click()
      

        pla.wait_new_page(enter_button, '/maps/%s' % id_map)

        enter_button = pla.xpath_finduniq(
            "//a[@href='/maps/%s/view' and "
            "normalize-space(text()) = 'View Map']" % id_map)
        enter_button.click()
        pla.wait_new_page(enter_button, '/maps/%s/view' % id_map, timeout=15)

        import time
        time.sleep(5)

        # <button id="ext-gen159" class=" x-btn-text gxp-icon-getfeatureinfo"
        # type="button">Identify
        enter_button = pla.xpath_finduniq(
            "//button[@type='button' and normalize-space(text())"
            "= 'Identify']", timeout=15)
        enter_button.click()

        # wait info button will be clicked
        pla.xpath_finduniq(
            "//button[@type='button' and normalize-space(text())"
            "= 'Identify']/../../../../..[contains(concat(' ', @class, ' '),"
            " ' x-btn-pressed ')]", timeout=15)

        _, x, y = pla.xpath_finduniq_coords(
            "//img[contains(@src, 'LAYERS=oqplatform%3Aghec_viewer_measure"
            "&FORMAT=image%2Fpng&TRANSPARENT=TRUE&SERVICE=WMS&VERSION="
            "1.1.1&REQUEST=GetMap&STYLES=&TILED=true&SRS=EPSG%3A900913&"
            "BBOX=-10018754.17,-10018754.17,0,0&WIDTH=256&HEIGHT=256')]",
            timeout=50)

        pla.add_click_event()
        pla.click_at(100 + x, 31 + y)

        pla.xpath_find_any("//div[text() = 'Third test item']", timeout=50)

        # Close geoexplorer popup
        close_popup = pla.xpath_finduniq(
            "//div[contains(concat(' ', @class, ' '),"
            " ' x-tool-close ')]", timeout=15)
        close_popup.click()
