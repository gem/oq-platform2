#!/usr/bin/env python
import unittest
from openquake.moon import platform_get

TIMEOUT = 100


class UserLoginTest(unittest.TestCase):

    def user_login_test(self):

        pla = platform_get()

        gem_user = 'GEM'
        gem_pwd = 'GEM'

        # New window with platform without other login
        plb = pla.platform_create(user=None, passwd=None)
        plb.init(landing='/', autologin=False)

        # New login
        input = plb.xpath_finduniq("//a[normalize-space(text()) = 'Sign in']")
        input.click()

        user_field = plb.xpath_find(
            "//form[@class='%s' or @class='%s']//input[@id="
            "'id_username' and @type='text' and @name='username']" % (
                ('sign-in', 'form-signin')))
        plb.wait_visibility(user_field, 2)
        user_field.send_keys(gem_user)

        passwd_field = plb.xpath_find(
            "//form[@class='%s' or @class='%s']//input[@id="
            "'id_password' and @type='password' and @name='password']" % (
                ('sign-in', 'form-signin')))
        plb.wait_visibility(passwd_field, 1)
        passwd_field.send_keys(gem_pwd)

        # <button class="btn pull-right" type="submit">Sign in</button>
        submit_button = plb.xpath_finduniq(
            "//button[@type='submit' and text()='%s']" %
            ("Sign in"))
        submit_button.click()

        # Check if user logged is correct
        check_user = plb.xpath_finduniq(
            "//img[@alt='GEM']", TIMEOUT)
        # "//a[@href='#' and"
        # " normalize-space(@class)='dropdown-toggle avatar']", TIMEOUT)
        # " and normalize-space(text())='%s']" % gem_user, TIMEOUT)
        check_user.click()

        pla.platform_destroy(plb)
