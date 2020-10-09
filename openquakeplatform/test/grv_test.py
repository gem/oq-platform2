#!/usr/bin/env python
import unittest
from selenium.webdriver.common.action_chains import ActionChains
from openquake.moon import platform_get

TIMEOUT = 100


class GrvTest(unittest.TestCase):

    def page_map_test(self):

        pla = platform_get()

        pla.get('/grv')

        pla.header_height_store(
            "//nav[@class='navbar navbar-inverse navbar-fixed-top']")

        content_map = pla.xpath_finduniq(
            "//div[@id='map']")

        action_chart = ActionChains(pla.driver)

        # click point to visualize economy graphic
        action_chart.move_to_element_with_offset(
            content_map, 550, 50).click().perform()

        # import time
        # time.sleep(50000)
        category_tabs = pla.xpath_finduniq(
            "//div[@id='categoryTabs']", TIMEOUT)

        # test fails if the svg is not found
        # economy_tabs = pla.xpath_finduniq(
        #     "//div[@id='economy']"
        #     "//div[@id='econ-chart-pcc']"
        #     "//*[name()='svg']/*[name()='g']"
        #     "/*[name()='g' and @class='foreground']"
        #     "/*[name()='path' and @class='Sweden']",
        #     el=category_tabs)

        # pla.scroll_into_view(economy_tabs)

        # import time
        # time.sleep(5000000)
