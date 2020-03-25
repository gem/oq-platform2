Openquake Platform
==================

Development Installation
------------------------

Install the following dependencies::

    for Ubuntu: postgresql-9.5-postgis-2.2 postgresql-9.5-postgis-scripts curl xmlstarlet supervisor numpy simplejson

Create a virtual environment::

    $ virtualenv platform

Clone the git repo::

    $ git clone https://github.com/gem/oq-platform2

Change directory to the downloaded repository directory::

    $ cd oq-platform2

Install PostgreSQL and PostGIS. For best results, stick with PostgreSQL 9.5
and PostGIS 2.2.

Install and run the application::

    $ pip install -e oq-platform2

(Optional.) Add bing maps api key to local_settings.py by modifying the BING_KEY flag.


Usage
-----

Once your development environment is set up, you can just run the application
from the `openquakeplatform` dir in the root of the git clone::

    $ source virtualenv/bin/activate  # to enable venv
    $ paver start -b 0.0.0.0:8000 # from platform folder

To stop the application at any time::

    $ paver stop

