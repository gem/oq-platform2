#!/usr/bin/env python
import unittest
from openquake.moon import platform_get


class MetadataTest(unittest.TestCase):

    def check_metadata_test(self):

        pla = platform_get()

        gem_user = 'GEM'                                                        
        gem_pwd = 'GEM'                                                         
                                                                                
        # New window with platform without other login                             
        plb = pla.platform_create(user=None, passwd=None)                          
        plb.init(landing='/', autologin=False)                                     
                                                                                
        # New login                                                             
        signin = plb.xpath_finduniq("//a[normalize-space(text()) = 'Sign in']") 
        signin.click()                         

        pla.get('/layer')

        # click on layer
        layer = pla.xpath_finduniq(
            "//a[normalize-space(text()) = 'ghec_viewer_measure']")
        layer.click()

        # click download metadata in layer page detail
        download_meta = pla.xpath_finduniq(
            "//button[@data-target = '#download-metadata']")
        download_meta.click()

        # click standard metadata
        standard_meta = pla.xpath_finduniq(
            "//a[normalize-space(text()) = 'Dublin Core']")
        standard_meta.click()
