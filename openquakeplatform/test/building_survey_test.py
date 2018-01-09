import unittest
from openquakeplatform.test import pla

TIMEOUT = 100


def div_sub():
    pla.xpath_finduniq(
        "//div[@name='sub']", TIMEOUT)


class BuildingSurveyTest(unittest.TestCase):

    def tutorial_test(self):

        tutorial_url = '/building-class/tutorial'

        # Redirect page of survey application
        pla.get(tutorial_url)

        # Check title
        pla.xpath_finduniq(
            "//h2[normalize-space(text())='Tutorial']")

        # Check video tutorial
        pla.xpath_finduniq(
                "//iframe[@id='gem-video'"
                " and @src='https://www.youtube.com/embed/bXrvc9Qzie4']")

    def new_classification_test(self):

        survey_url = '/building-class'

        # Redirect page of survey application
        pla.get(survey_url)

        # Select zone
        zone_field = pla.xpath_finduniq(
            "//select[@id='country-id']"
            "/option[normalize-space(text())='French Guiana']")
        zone_field.click()

        # Click button new classification
        new_classif = pla.xpath_finduniq(
            "//button[@id='new-classification']", TIMEOUT, True)
        new_classif.click()

        # Choose occupancy healthcare
        check_occupancy = pla.xpath_finduniq(
            "//input[@name='occupancy' "
            "and @type='radio' and @value='healthcare']", TIMEOUT)
        check_occupancy.click()

        # Occupancy next button
        occup_next = pla.xpath_finduniq(
            "//button[@class='occup_next_btn'"
            " and normalize-space(text())='next']", TIMEOUT)
        occup_next.click()

        # Choose material
        check_material = pla.xpath_finduniq(
            "//input[@name='Steel' and @type='checkbox']")
        check_material.click()

        # Choose type of material
        material_type = pla.xpath_finduniq(
            "//input[@name='Cold formed members' and @type='checkbox']",
            TIMEOUT)
        material_type.location_once_scrolled_into_view  # scroll,found element
        material_type.click()

        # Choose type of material
        connection_material = pla.xpath_finduniq(
            "//input[@name='Bolted connection' and @type='checkbox']", TIMEOUT)
        connection_material.location_once_scrolled_into_view
        connection_material.click()

        # # Lateral load resisting system of material
        lateral_material = pla.xpath_finduniq(
            "//input[@name='Dual system' and @type='checkbox']", TIMEOUT)
        lateral_material.location_once_scrolled_into_view
        lateral_material.click()

        # Height material
        height_material = pla.xpath_finduniq(
            "//input[@name='Tall (>12 floors)'"
            " and @type='checkbox']", TIMEOUT, True)
        height_material.click()

        # Irregularities
        irreg_material = pla.xpath_finduniq(
            "//input[@name='Irregular-soft storey' and @type='checkbox']",
            TIMEOUT)
        irreg_material.click()

        # Ductility
        duct_material = pla.xpath_finduniq(
            "//input[@name='High ductility (PGA>0.3g)' and @type='checkbox']")
        duct_material.click()

        # Occupancy save button
        occup_save = pla.xpath_finduniq(
            "//button[@name='save'"
            " and normalize-space(text())='save']", TIMEOUT)
        occup_save.click()

        # Redirect page of survey application
        # pla.get(survey_url)
        # pla.driver.switch_to.alert.accept()
