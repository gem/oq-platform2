#!/usr/bin/env python
import unittest
from openquake.moon import platform_get
from selenium.webdriver.common.action_chains import ActionChains

TIMEOUT = 100


class SearchTest(unittest.TestCase):
    def search_test(self):

        pla = platform_get()

        pla.get('')

        search_input = 'assumpcao2014'

        # Search from header
        #
        # click search icon
        click_ico = pla.xpath_finduniq(
            "//a[@href='javascript:void(0)']"
            "/img[@src='/static/geonode/img/oq-search.png']",
            TIMEOUT, 1)
        click_ico.click()

        # write on search input
        search = pla.xpath_findfirst(
            "//input[@id='search_input' and @placeholder='Search']",
            TIMEOUT, 1)
        search.clear()
        search.send_keys(search_input)

        # launch search_element method
        auto_complete = pla.xpath_findfirst(
            "//span[@class='yourlabs-autocomplete']"
            "/span[normalize-space(text())='assumpcao2014']",
            TIMEOUT, 1)
        actionChains = ActionChains(pla.driver)
        actionChains.double_click(auto_complete).perform()

        pla.xpath_findfirst(
            "//a[@href='/layers/oqplatform:assumpcao2014']",
            TIMEOUT, 1)

        # Search from left sidebar
        #
        # page list maps
        pla.get('/layers')

        # write on search input
        left_search = pla.xpath_findfirst(
            "//input[@id='text_search_input'"
            " and @placeholder='Search by title']",
            TIMEOUT, 1)
        left_search.clear()
        left_search.send_keys(search_input)

        # launch search_element method
        left_search_button = pla.xpath_findfirst(
            "//button[@class='btn btn-primary' and @id='text_search_btn']",
            TIMEOUT, 1)
        left_search_button.click()

        pla.xpath_findfirst(
            "//a[@href='/layers/oqplatform:assumpcao2014']",
            TIMEOUT, 1)
