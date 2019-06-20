#!/usr/bin/env python
import os
import subprocess
import unittest
from openquake.moon import platform_get

TIMEOUT = 100


def restart_apache():

    # set if is production installation
    prod = os.getenv("OQ_TEST")

    # restart apache
    if prod == "y":
        # restart apache
        subprocess.check_call(
            "geonode collectstatic --noinput --verbosity 0".split())
        subprocess.check_call("sudo service apache2 restart".split())
    else:
        pass


class TilestreamTest(unittest.TestCase):

    def tilestream_test(self):

        # change content GETJson in Tilestream Source.js
        s = open(
                "/home/ubuntu/oq-platform2/openquakeplatform/"
                "static/js/TileStreamSource.js").read()
        s = s.replace('Tileset', 'TilesetT')
        r = open(
                "/home/ubuntu/oq-platform2/openquakeplatform/"
                "static/js/TileStreamSource.js", 'w')
        r.write(s)
        r.close()

        restart_apache()

        pla = platform_get()

        pla.get('/explore')
        pla.wait_new_page("//b[contains(text(),"
                          " 'Seismic Hazard Data Sets and Models')]",
                          "/explore", strategy="next", timeout=15)

        enter_button = pla.xpath_finduniq(
            "//li/a[normalize-space(text()) = 'Global "
            "Instrumental Earthquake Catalogue (1900 - 2009)']")

        href = enter_button.get_attribute('href')
        id_map = os.path.basename(href)
        enter_button.click()

        enter_button_view = pla.xpath_finduniq(
            "//a[@href='/maps/%s/view' and "
            "normalize-space(text()) = 'View Map']" % id_map)
        enter_button_view.click()

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

        pla.xpath_finduniq("//div[text() = '1942-02-09T07:11:00']", timeout=50)

        # return content GETJson in Tilestream Source.js
        s = open(
                "/home/ubuntu/oq-platform2/openquakeplatform/"
                "static/js/TileStreamSource.js").read()
        s = s.replace('TilesetT', 'Tileset')
        r = open(
                "/home/ubuntu/oq-platform2/openquakeplatform/"
                "static/js/TileStreamSource.js", 'w')
        r.write(s)
        r.close()

        restart_apache()
