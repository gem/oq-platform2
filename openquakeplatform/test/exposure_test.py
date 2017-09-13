#!/usr/bin/env python
import os
import unittest
from openquakeplatform.test import pla

url_exp = "/exposure"

class ExposureTest(unittest.TestCase):

    def load_data_region_test(self):
        
        pla.get(url_exp)

        clickldbyreg = pla.xpath_finduniq(
                     "//button[@id='countries-list']",
                     100, 1)
        clickldbyreg.click()

        # click paging

        page25 = pla.xpath_finduniq(
               "//button/span[normalize-space(text())='25']",
               100, 1)
        page25.click()

        # click nation

        class_tr = "Angola18"

        clicknation = pla.xpath_finduniq(
                    "//table/tbody/tr[contains(@class, '%s')]" % class_tr )     
        clicknation.click()

        # click second level nation

        text_td = "Cabinda"

        leveltwo = pla.xpath_finduniq(
                 "//table/tbody//td[contains(text(), '%s')]" % text_td )      
        leveltwo.click()   
       
        # click download csv

        downreg = pla.xpath_finduniq(
                "//button[@id='subDwellingFractionsDownload']"
                "/span[normalize-space(text())='Download']",
                100, 1)
        downreg.click()
        
        # click download nrml or csv

        downsubnat = pla.xpath_finduniq(
                   "//button[@id='subNationalExposureBldgDownload']"
                   "/span[normalize-space(text())='Download']",
                   100, 1)
        downsubnat.click()