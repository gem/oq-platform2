#!/usr/bin/env python
import unittest
from openquake.moon import platform_get
from selenium.webdriver.common.action_chains import ActionChains

TIMEOUT = '100'


class SearchTest(unittest.TestCase):
    def search_test(self):

        pla = platform_get('')

        search_input = 'assumpcao2014'

        # click search icon on header
        click_ico = pla.xpath_finduniq(
            "//a[@href='javascript:void(0)']"
            "/img[@src='/static/geonode/img/oq-search.png']",
            100, 1)
        click_ico.click()

        # write on serach input
        search = pla.xpath_findfirst(
            "//input[@id='search_input' and placeholder='Search']",
            TIMEOUT, 1)
        search.clear()
        search.send_keys(search_input)

        auto_complete_click = pla.xpath_findfirst(
            "//span[@class='yourlabs-autocomplete']"
            "/span[normalize-space(text())='assumpcao2014']",
            TIMEOUT, 1)
        actionChains = ActionChains(pla.driver)
        actionChains.double_click(auto_complete_click).perform()

        pla.wait_new_page(
            auto_complete_click,
            'search/?title__icontains=assumpcao2014&limit=100&offset=0',
            timeout=10)

        # check title and content in search page
        pla.xpath_finduniq(
            "//h2[normalize-space(text())='assumpcao2014']",
            100, 1)

        pla.xpath_finduniq(
            "//a[@ng-if='item.detail_url.indexOf('/layers/') > -1' "
            "and @href='/layers/oqplatform:assumpcao2014']",
            100, 1)
