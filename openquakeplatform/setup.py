import os
from setuptools import setup, find_packages

from openquakeplatform import __version__ as oqp_version


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name="openquakeplatform",
    version=oqp_version,
    author="",
    author_email="",
    description="openquakeplatform, based on GeoNode",
    long_description=(read('README.rst')),
    # Full list of classifiers can be found at:
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta'
    ],
    license="BSD",
    keywords="openquakeplatform geonode django",
    url='https://github.com/gem/oq-platform2',
    packages=['openquakeplatform',
              'openquakeplatform.isc_viewer',
              'openquakeplatform.ghec_viewer',
              'openquakeplatform.exposure',
              'openquakeplatform.world',
              'openquakeplatform.svir',
              'openquakeplatform.vulnerability',
              'openquakeplatform.weblib',
              'openquakeplatform.weblib.baseclasses',
              'openquakeplatform.grv',
              'openquakeplatform.hazus',
              'openquakeplatform.irv',
              'openquakeplatform.test',
              ],
    # NOTE:  django-chained-multi-checkboxes
    #        is following the new convention: a floating tag on github
    #        v<major>.<minor> only follows
    #        the lifecicle of all the bugfix versions of the repository
    #        and pip depends on it.
    #        Follow the same rule for all the other gem dependencies when
    #        an update is needed.
    # ATTENTION: Please, do not split following lines,
    #            the deploy.sh script manages them automatically.
    dependency_links = ['http://github.com/gem/django-chained-selectbox.git@pla26#egg=django-chained-selectbox-0.2.2',
                        'http://github.com/gem/django-nested-inlines.git@pla26#egg=django-nested-inlines-0.1.4',
                        'http://github.com/gem/django-chained-multi-checkboxes.git@pla26#egg=django-chained-multi-checkboxes-0.4.1',
                        'http://github.com/gem/wadofstuff-django-serializers.git@pla26#egg=wadofstuff-django-serializers-1.1.2',
                        ],
    install_requires=[
        "amqp >= 1.4.9 , < 1.5",
        "anyjson >= 0.3.3 , < 0.4",
        "awesome-slugify >= 1.6.2 , < 1.7",
        "beautifulsoup4 >= 4.2.1 , < 4.3",
        "billiard >= 3.3.0.23 , < 3.4",
        "boto >= 2.38.0 , < 2.39",
        "celery >= 3.1.18 , < 3.2",
        "certifi >= 2017.7.27.1 , < 2017.8",
        "dj-database-url >= 0.4.2 , < 0.5",
        "Django >= 1.8.7 , < 1.9",
        "django-activity-stream >= 0.6.1 , < 0.7",
        "django-appconf >= 0.5 , < 0.6",
        "django-autocomplete-light >= 2.3.3 , < 2.4",
        "django-bootstrap3-datetimepicker >= 2.2.3 , < 2.3",
        "django-braces >= 1.11.0 , < 1.12",
        "django-celery >= 3.1.16 , < 3.2",
        "django-downloadview >= 1.2 , < 1.3",
        "django-extensions >= 1.6.1 , < 1.7",
        "django-forms-bootstrap >= 3.0.1 , < 3.1",
        "django-friendly-tag-loader >= 1.2.1 , < 1.3",
        "django-geoexplorer >= 4.0.5 , < 4.1",
        "django-geonode-client >= 0.0.15 , < 0.1",
        "django-guardian >= 1.4.6 , < 1.5",
        "django-haystack >= 2.4.1 , < 2.5",
        "django-jsonfield >= 0.9.16 , < 0.10",
        "django-jsonfield-compat >= 0.4.4 , < 0.5",
        "django-leaflet >= 0.13.7 , < 0.14",
        "django-modeltranslation >= 0.12 , < 0.13",
        "django-mptt >= 0.8.6 , < 0.9",
        "django-nose >= 1.4.4 , < 1.5",
        "django-oauth-toolkit >= 0.12.0 , < 0.13",
        "django-pagination >= 1.0.7 , < 1.1",
        "django-polymorphic >= 0.9.2 , < 0.10",
        "django-storages >= 1.1.8 , < 1.2",
        "django-taggit >= 0.21.0 , < 0.22",
        "django-tastypie >= 0.12.2 , < 0.13",
        "django-treebeard >= 3.0 , < 3.1",
        "elasticsearch >= 2.4.0 , < 2.5",
        "flake8 >= 2.3.0 , < 2.4",
        "geolinks >= 0.2.0 , < 0.3",
        "geonode-agon-ratings >= 0.3.5 , < 0.4",
        "geonode-announcements >= 1.0.8 , < 1.1",
        "geonode-arcrest >= 10.2 , < 10.3",
        "geonode-avatar >= 2.1.6 , < 2.2",
        "geonode-dialogos >= 0.7 , < 0.8",
        "geonode-notification >= 1.1.1 , < 1.2",
        "geonode-user-accounts >= 1.0.13 , < 1.1",
        "geonode-user-messages >= 0.1.5 , < 0.2",
        "gisdata >= 0.5.4 , < 0.6",
        "gsconfig >= 1.0.6 , < 1.1",
        "gsimporter >= 1.0.0 , < 1.1",
        "httplib2 >= 0.9.2 , < 0.10",
        "kombu >= 3.0.35 , < 3.1",
        "lxml >= 3.6.4 , < 3.7",
        "mccabe >= 0.5.2 , < 0.6",
        "MultipartPostHandler >= 0.1.0 , < 0.2",
        "nose >= 1.3.7 , < 1.4",
        "numpy >= 1.13.1 , < 1.14",
        "oauthlib >= 2.0.1 , < 2.1",
        "OWSLib >= 0.11.0 , < 0.12",
        "Paver >= 1.2.4 , < 1.3",
        "pep8 >= 1.6.2 , < 1.7",
        "Pillow >= 3.3.1 , < 3.4",
        "pinax-theme-bootstrap >= 3.0a11 , < 3.1",
        "pinax-theme-bootstrap-account >= 1.0b2 , < 1.1",
        "pkg-resources >= 0.0.0 , < 0.1",
        "psycopg2 >= 2.7.3.1 , < 2.8",
        "pycsw >= 2.0.2 , < 2.1",
        "pyelasticsearch >= 1.4 , < 1.5",
        "pyflakes >= 1.2.3 , < 1.3",
        "pyproj >= 1.9.5.1 , < 1.10",
        "python-dateutil >= 2.5.3 , < 2.6",
        "python-mimeparse >= 1.5.2 , < 1.6",
        "pytz >= 2016.6.1 , < 2016.7",
        "PyYAML >= 3.11 , < 3.12",
        "regex >= 2016.7.21 , < 2016.8",
        "requests >= 2.11.1 , < 2.12",
        "selenium >= 3.5.0 , < 3.9",
        "Shapely >= 1.5.17 , < 1.6",
        "simplejson >= 3.11.1 , < 3.12",
        "six >= 1.10.0 , < 1.11",
        "transifex-client >= 0.10 , < 0.11",
        "Unidecode >= 0.4.19 , < 0.5",
        "urllib3 >= 1.22 , < 1.23",
        "xmltodict >= 0.9.2 , < 0.10",
    ],
    include_package_data=True,
    zip_safe=False,
)
