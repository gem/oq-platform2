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

import re
import sys
from setuptools import setup, find_packages, Extension

def get_version():
    version_re = r"^__version__\s+=\s+['\"]([^'\"]*)['\"]"
    version = None

    package_init = 'openquake/moon/__init__.py'
    for line in open(package_init, 'r'):
        version_match = re.search(version_re, line, re.M)
        if version_match:
            version = version_match.group(1)
            break
    else:
        sys.exit('__version__ variable not found in %s' % package_init)

    return version
version = get_version()

url = "http://github.com/gem/oq-moon"

README = """
openquake.moon is a selenium wrapper to handle more confortably tests.

Copyright (C) 2016 GEM Foundation
"""

setup(
    name='openquake.moon',
    version=version,
    description="openquake.moon is a selenium wrapper to handle"
    " more confortably tests.",
    long_description=README,
    url=url,
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'selenium'
    ],
    author='GEM Foundation',
    author_email='devops@openquake.org',
    maintainer='GEM Foundation',
    maintainer_email='devops@openquake.org',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering',
    ),
    keywords="selenium test",
    license="AGPL3",
    platforms=["any"],
    namespace_packages=['openquake'],
    zip_safe=False,
)
