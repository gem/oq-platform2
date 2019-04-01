#!/usr/bin/env python
import unittest
import os
from openquake.moon import platform_get


class IscTest(unittest.TestCase):
    def isc_test(self):

        pla = platform_get()

        pla.get('/explore')
        pla.wait_new_page("//b[contains(text(),"
                          " 'Seismic Hazard Data Sets and Models')]",
                          "/explore", strategy="next", timeout=15)

        # <li>
        # <a href="/maps/23">
        enter_button = pla.xpath_finduniq(
            "//li/a[normalize-space(text()) = 'Global "
            "Instrumental Earthquake Catalogue (1900 - 2009)']")

        href = enter_button.get_attribute('href')
        id_map = os.path.basename(href)
        enter_button.click()
        # pla.driver.refresh()
        pla.driver.execute_script("location.reload()")
        pla.wait_new_page(enter_button, '/maps/%s' % id_map, timeout=30)

        enter_button_view = pla.xpath_finduniq(
            "//a[@href='/maps/%s/view' and "
            "normalize-space(text()) = 'View Map']" % id_map)
        enter_button_view.click()
        pla.driver.execute_script("location.reload()")
        # pla.driver.refresh()
        pla.wait_new_page(enter_button_view, '/maps/%s/view' % id_map, timeout=30)

        # <button id="ext-gen159" class=" x-btn-text gxp-icon-getfeatureinfo"
        # type="button">Identify
        enter_button_ident = pla.xpath_finduniq(
            "//button[@type='button' and normalize-space(text())"
            "= 'Identify']", timeout=20)
        enter_button_ident.click()

        # wait info button will be clicked
        pla.xpath_finduniq(
            "//button[@type='button' and normalize-space(text())"
            "= 'Identify']/../../../../..[contains(concat(' ', @class, ' '),"
            " ' x-btn-pressed ')]", timeout=20)

        _, x, y = pla.xpath_finduniq_coords(
            "//img[contains(@src, 'LAYERS=oqplatform%3Aisc_viewer_measure"
            "&FORMAT=image%2Fpng&TRANSPARENT=TRUE&SERVICE=WMS&VERSION="
            "1.1.1&REQUEST=GetMap&STYLES=&TILED=true&SRS=EPSG%3A900913&"
            "BBOX=-5009377.085,0,0,5009377.085&WIDTH=256&HEIGHT=256')]",
            timeout=50)

        pla.add_click_event()
        pla.click_at(107 + x, 70 + y)

        pla.xpath_finduniq("//div[text() = '1942-02-09T12:11:00']", timeout=50)
