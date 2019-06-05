#!/usr/bin/env python
import unittest
from openquake.moon import platform_get
from selenium.webdriver.common.action_chains import ActionChains

TIMEOUT = 100


def search_element():

    pla = platform_get()

    auto_complete_click = pla.xpath_findfirst(
        "//span[@class='yourlabs-autocomplete']"
        "/span[normalize-space(text())='assumpcao2014']",
        TIMEOUT, 1)
    actionChains = ActionChains(pla.driver)
    actionChains.double_click(auto_complete_click).perform()

    pla.wait_new_page(
        auto_complete_click,
        # '/search/?title__icontains=assumpcao2014&limit=100&offset=0',
        '/search/?title__icontains=assumpcao2014',
        timeout=10)

    pla.xpath_finduniq(
        "//a[@ng-if='item.detail_url.indexOf("'/layers/'") > -1'"
        " and @href='/layers/oqplatform:assumpcao2014']",
        TIMEOUT, 1)


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
        search_element()

        # Search from left sidebar
        #
        # page list maps
        pla.get('/maps')

        # write on search input
        left_search = pla.xpath_findfirst(
            "//input[@id='text_search_input'"
            " and @placeholder='Search by text']",
            TIMEOUT, 1)
        left_search.clear()
        left_search.send_keys(search_input)

        # launch search_element method
        search_element()
