#!/usr/bin/env python
import unittest
from openquake.moon import platform_get
from selenium.webdriver.common.keys import Keys

# path exposure
url_exp = "/exposure"


class ExposureTest(unittest.TestCase):

    def load_data_region_test(self):

        pla = platform_get()

        # go to first page
        pla.get(url_exp)

        clickldbyreg = pla.xpath_finduniq(
            "//button[@id='countries-list']",
            100, 1)
        clickldbyreg.click()

        # click paging
        nation = "Algeria"

        # Search city
        search_nation = pla.xpath_finduniq(
            "//input[@class='input-filter form-control ng-pristine "
            "ng-valid ng-scope ng-touched' and @type='text']")
        search_nation.send_keys(nation, Keys.ENTER)

        page25 = pla.xpath_finduniq(
            "//button/span[normalize-space(text())='25']",
            100, 1)
        page25.click()

        # click nation
        clicknation = pla.xpath_finduniq(
            "//table/tbody//td[@class='ng-binding'"
            " and contains(text(), '%s')]" % nation)
        clicknation.click()

        # click download csv of fractions
        downreg = pla.xpath_finduniq(
            "//button[@id='dwellingFractionsDownload']"
            "/span[normalize-space(text())='Download']",
            100, 1)
        downreg.click()

        # click download nrml or csv of sub-national
        downsubnat = pla.xpath_finduniq(
            "//button[@id='nationalExposureBldgDownload']"
            "/span[normalize-space(text())='Download']",
            100, 1)
        downsubnat.click()

        # close final windows
        close_win_wait_download = pla.xpath_finduniq(
            "//button["
            "../span[normalize-space(text())='Download']"
            " and @title='close']",
            100, 1)
        close_win_wait_download.click()

        # return to first page
        pla.get(url_exp)
