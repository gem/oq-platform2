#!/usr/bin/env python
# import os
import unittest
from openquakeplatform.test import pla
from selenium.webdriver.common.keys import Keys


class SurveyTest(unittest.TestCase):

    def watch_tut_test(self):

        # calculate
        wat = pla.xpath_finduniq(
            "//a[normalize-space(text())='watch tutorial here']",
            100, 1)
        wat.click()

        pla.wait_new_page(wat, '/building-class/tutorial', timeout=10)

    def new_class_test(self):

        select = pla.xpath_finduniq(
               "//select[@id='country-id']/option[text()='Anguilla']",
               100, 1)
        select.click()
      
        choice_new = pla.xpath_finduniq(
                   "//button[@id='new-classification']", 
                   100, 1)
        choice_new.click()
