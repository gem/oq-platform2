# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2016 GEM Foundation
#
# OpenQuake Moon (oq-moon) is free software: you can redistribute it
# and/or modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenQuake Moon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.

import os
import sys

from nose.plugins import Plugin
from selenium.common.exceptions import (NoAlertPresentException,
                                        UnexpectedAlertPresentException,
                                        )


class FailureCatcher(Plugin):
    name = 'failurecatcher'
    prefix = ""
    enabled = False

    def options(self, parser, env=os.environ):
        parser.add_option('--failurecatcher',
                          action="store", dest="failurecatcher_prefix",
                          default="", help="prefix for any output file")

    def configure(self, options, conf):
        if options.failurecatcher_prefix:
            self.enabled = True
            self.prefix = options.failurecatcher_prefix
        super(FailureCatcher, self).configure(options, conf)

    # uncomment this method to screenshot successful tests too
    # def addSuccess(self, test):
    #     from openquakeplatform.test import pla
    #     pla.screenshot('%s_%s.png' % (self.prefix, test.id()))
    #

    @classmethod
    def alert_manager(cls, pla):
        # selenium can't take a screenshot if an alert is displayed
        try:
            alert = pla.switch_to_alert()
            sys.stderr.write("Found alert during cleanup: [%s]\n" % alert.text)
            alert.accept()
        except (NoAlertPresentException, UnexpectedAlertPresentException, AttributeError):
            pass

    def addError(self, test, err):
        from openquake.moon import Moon
        primary = Moon.primary_get()
        if primary is not None:
            self.alert_manager(primary)
            primary.screenshot('%s_%s.png' % (self.prefix, test.id()))

    def addFailure(self, test, err):
        from openquake.moon import Moon
        primary = Moon.primary_get()
        if primary is not None:
            self.alert_manager(primary)
            primary.screenshot('%s_%s.png' % (self.prefix, test.id()))

    def describeTest(self, test):
        return "%s" % test.id()
