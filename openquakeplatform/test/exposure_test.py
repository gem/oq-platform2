#!/usr/bin/env python
import os
import unittest
from openquakeplatform.test import pla
from selenium.webdriver.common.keys import Keys
import time

url_exp = "/exposure"

class ExposureTest(unittest.TestCase):

    def load_data_region_test(self):
        
        pla.get(url_exp)

        clickldbyreg = pla.xpath_finduniq(
                     "//button[@id='countries-list']",
                     100, 1)
        clickldbyreg.click()

        # time.sleep(5)

        page25 = pla.xpath_finduniq(
               "//button/span[normalize-space(text())='25']",
               100, 1)
        page25.click()

        # time.sleep(5)

        class_tr = "Angola18"

        clicknation = pla.xpath_finduniq(
                    "//table/tbody/tr[contains(@class, '%s')]" % class_tr )     
        clicknation.click()

        # time.sleep(5)

        class_td = "Cabinda"

        leveltwo = pla.xpath_finduniq(
                 "//table/tbody//td[contains(text(), '%s')]" % class_td )      
        leveltwo.click()   
       
        # time.sleep(5)

        downreg = pla.xpath_finduniq(
                "//button[@id='subDwellingFractionsDownload']"
                "/span[normalize-space(text())='Download']",
                100, 1)
        downreg.click()
        # alert = pla.driver.switch_to.alert.accept()
        
        downsubnat = pla.xpath_finduniq(
                   "//button[@id='subNationalExposureBldgDownload']"
                   "/span[normalize-space(text())='Download']",
                   100, 1)
        downsubnat.click()
