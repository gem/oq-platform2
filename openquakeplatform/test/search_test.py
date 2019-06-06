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
        action = actionChains.double_click(auto_complete).perform()

        pla.wait_new_page(
            action,
            '/search/?title__icontains=assumpcao2014',
            timeout=10)

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
            " and @placeholder='Search by text']",
            TIMEOUT, 1)
        left_search.clear()
        left_search.send_keys(search_input)

        # launch search_element method
        left_auto_complete = pla.xpath_findfirst(
            "//span[@class='yourlabs-autocomplete']"
            "/span[normalize-space(text())='assumpcao2014']",
            TIMEOUT, 1)
        actionChains = ActionChains(pla.driver)
        left_action = actionChains.double_click(left_auto_complete).perform()

        pla.wait_new_page(
            left_action,
            '/layers/?limit=100&offset=0&title__icontains=assumpcao2014',
            timeout=10)

        pla.xpath_findfirst(
            "//a[@href='/layers/oqplatform:assumpcao2014']",
            TIMEOUT, 1)
