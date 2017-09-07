#!/usr/bin/env python
# import os
import unittest
from openquakeplatform.test import pla
from selenium.webdriver.common.keys import Keys

b_url = "/building-class"


class SurveyTest(unittest.TestCase):

    def watch_tut_test(self):

        pla.get(b_url)

        wat = pla.xpath_finduniq(
            "//a[normalize-space(text())='watch tutorial here']",
            100, 1)
        wat.click()

        pla.wait_new_page(wat, '/building-class/tutorial', timeout=10)

    def new_class_test(self):

        pla.get(b_url)

        select = pla.xpath_finduniq(
               "//select[@id='country-id']/option[text()='Anguilla']",
               100, 1)
        select.click()

        choice_new = pla.xpath_finduniq(
                   "//button[@id='new-classification']",
                   100, 1)
        choice_new.click()

        occupancy = pla.xpath_finduniq(
                  "//input[@value='industrial' and @type='radio']")
        occupancy.click()

        choice_next = pla.xpath_finduniq(
                    "//button[@name='next']",
                    100, 1)
        choice_next.click()

        choice_material = pla.xpath_finduniq(
                        "//input[@name='steel' and @type='checkbox']",
                        100, 1)
        choice_material.click()

        choice_steel = pla.xpath_finduniq(
                     "//input[@name='Cold formed members'"
                     " and @type='checkbox']",
                     100, 1)
        choice_steel.click()

        type_conn = pla.xpath_finduniq(
                  "//input[@name='Riveted' and @type='checkbox']",
                  100, 1)
        type_conn.click()

        llrsyst = pla.xpath_finduniq(
                "//input[@name='Wall' and @type='checkbox']",
                100, 1)
        llrsyst.click()

        height = pla.xpath_finduniq(
               "//input[@name='High-rise (7-12 floors)'"
               " and @type='checkbox']",
               100, 1)
        height.click()

        irreg = pla.xpath_finduniq(
              "//input[@name='Regular' and @type='checkbox']",
              100, 1)
        irreg.click()

        duct = pla.xpath_finduniq(
             "//input[@name='Non ductile (PGA<0.1g)' and @type='checkbox']",
             100, 1)

        duct.click()

        save = pla.xpath_finduniq(
             "//button[@name='save']",
             100, 1)
        save.click()

        # result
        pla.xpath_finduniq(
            "//div[normalize-space(text())='success'"
            " and @class='save_resp_ok']",
            100, 1)

        delete = pla.xpath_finduniq(
               "//button[@type='button' and @name='delete']",
               100, 1)
        delete.click()
